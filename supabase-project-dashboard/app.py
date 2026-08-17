#
# To test this app locally:
#   cd "C:\Users\Dan\Documents\GitHub\Metrics\supabase-project-dashboard"
#   python -m streamlit run app.py
#

import streamlit as st
import pandas as pd
import os
import json
from dotenv import load_dotenv
from supabase_client import get_supabase_client

# Load environment variables from .env file (local development)
load_dotenv()

# Helper function to get config from either .env or Streamlit secrets
def get_config(key, default=''):
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

st.set_page_config(
    page_title="CPI Project Takeoff Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load config values
supabase_url = get_config('SUPABASE_URL', '')
supabase_key = get_config('SUPABASE_KEY', '')

# Configuration is loaded from .env or .streamlit/secrets.toml

# Main app logic
if not supabase_url or not supabase_key:
    st.warning("⚠️ Please set your Supabase credentials in .streamlit/secrets.toml or the .env file.")
    st.info("You can find these credentials in your Supabase project API settings.")
else:
    # Initialize Supabase client
    try:
        supabase = get_supabase_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {str(e)}")
        st.stop()

    

    try:
        # Fetch project list from project_data table
        try:
            all_projects = supabase.select("project_data", limit=10000)
            if not all_projects:
                st.sidebar.warning("⚠️ project_data: 0 rows (check RLS policies)")
        except Exception as project_error:
            st.sidebar.error(f"❌ project_data error: {str(project_error)}")
            all_projects = None
        
        if not all_projects:
            st.warning("⚠️ No data found in project_data table")
            st.info("""
            **Possible causes:**
            1. **RLS (Row Level Security)** policies may be blocking access
            2. Table is empty or doesn't exist
            3. Wrong credentials or permissions
            
            **Next steps:**
            - Check Supabase dashboard to verify table has data
            - Check RLS policies on the `project_data` table
            - Try disabling RLS temporarily for testing
            """)
            st.stop()
        
        # Convert to DataFrame
        df_projects = pd.DataFrame(all_projects)
        
        # Validate project_id column exists
        if "project_id" not in df_projects.columns:
            st.error("❌ 'project_id' column not found in project_data table")
            st.info("Available columns: " + ", ".join(df_projects.columns.tolist()))
            st.stop()
        
        # Get unique project_ids from project_data table
        project_ids = sorted(df_projects["project_id"].dropna().unique().tolist())
        
        if not project_ids:
            st.warning("⚠️ No project_ids found in the data")
            st.stop()
        
        # Project selector in sidebar
        with st.sidebar:
            st.markdown("### � Project")
            selected_project = st.selectbox(
                "Select project:",
                options=project_ids,
                index=0,
                label_visibility="collapsed"
            )
        
        st.title(f"📈 {selected_project}")

        # Fetch rhino tables filtered by selected project with pagination
        def fetch_all_pages(table, filters, page_size=1000):
            all_rows = []
            offset = 0
            while True:
                page = supabase.select(
                    table,
                    filters=filters,
                    limit=page_size,
                    offset=offset,
                )
                if not page:
                    break
                all_rows.extend(page)
                if len(page) < page_size:
                    break
                offset += page_size
            return all_rows

        try:
            all_blocks = fetch_all_pages("rhino_blocks", {"project_id": selected_project})
        except Exception as block_error:
            st.sidebar.error(f"❌ rhino_blocks error: {str(block_error)}")
            all_blocks = None

        try:
            all_breps = fetch_all_pages("rhino_breps", {"project_id": selected_project})
            if not all_breps:
                st.sidebar.warning("⚠️ rhino_breps: 0 rows (check RLS policies)")
        except Exception as brep_error:
            st.sidebar.error(f"❌ rhino_breps error: {str(brep_error)}")
            all_breps = None

        df_blocks_filtered = pd.DataFrame(all_blocks) if all_blocks else pd.DataFrame()
        df_breps_filtered = pd.DataFrame(all_breps) if all_breps else pd.DataFrame()
        
        # ============================================================
        # SECTION 1: TAKEOFF DATA
        # ============================================================
        st.markdown("## 📊 Takeoff Data")
        st.markdown("---")
        
        # BREPs Summary Section (filtered by selected project)
        st.markdown("### 🌲 Timber Summary")
        if not df_breps_filtered.empty:
            # Calculate summary metrics
            total_breps = len(df_breps_filtered)
            unique_batches = df_breps_filtered["batch_id"].nunique() if "batch_id" in df_breps_filtered.columns else 0
            
            # Display metrics in columns
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Timber elements", total_breps)
            col2.metric("Batches", unique_batches)
            
            # Show latest batch if available
            if "batch_id" in df_breps_filtered.columns:
                latest_batch = df_breps_filtered["batch_id"].max()
                col3.metric("Latest Batch", str(latest_batch))
            
            # Show expandable detailed view
            with st.expander("Timber Table Details", expanded=False):
                # Extract selected fields from the rhino_breps table
                detail_base_cols = ["project_id", "brep_name", "user_text"]
                detail_base_cols = [c for c in detail_base_cols if c in df_breps_filtered.columns]
                df_details = df_breps_filtered[detail_base_cols].copy()

                user_text_keys = [
                    "KS-Material",
                    "KS-Element spec",
                    "SZ-Cross section inches",
                    "SZ-Volume",
                    "MA-Tag",
                    "MA-Fabricator",
                ]

                def _get_user_text_val(user_text, key):
                    if isinstance(user_text, dict):
                        return user_text.get(key)
                    if isinstance(user_text, str):
                        try:
                            parsed = json.loads(user_text)
                            if isinstance(parsed, dict):
                                return parsed.get(key)
                        except Exception:
                            pass
                    return None

                if "user_text" in df_details.columns:
                    for key in user_text_keys:
                        df_details[key] = df_details["user_text"].apply(
                            lambda x: _get_user_text_val(x, key)
                        )

                # Display only the requested columns
                display_cols = ["project_id", "brep_name"] + user_text_keys
                display_cols = [c for c in display_cols if c in df_details.columns]
                st.dataframe(df_details[display_cols], width="stretch", hide_index=True)

            # Volume and piece count summary by MA-Description
            with st.expander("Volume & Piece Count by Description", expanded=False):
                if "user_text" in df_breps_filtered.columns:
                    desc_key = "MA-Description"
                    vol_key = "SZ-Volume"

                    def _get_user_text_val(user_text, key):
                        if isinstance(user_text, dict):
                            return user_text.get(key)
                        if isinstance(user_text, str):
                            try:
                                parsed = json.loads(user_text)
                                if isinstance(parsed, dict):
                                    return parsed.get(key)
                            except Exception:
                                pass
                        return None

                    df_summary = df_breps_filtered.copy()
                    df_summary[desc_key] = df_summary["user_text"].apply(
                        lambda x: _get_user_text_val(x, desc_key)
                    )
                    df_summary[vol_key] = pd.to_numeric(
                        df_summary["user_text"].apply(
                            lambda x: _get_user_text_val(x, vol_key)
                        ),
                        errors="coerce",
                    )
                    df_summary = df_summary.dropna(subset=[desc_key])

                    if not df_summary.empty:
                        summary_counts = (
                            df_summary.groupby(desc_key)
                            .size()
                            .reset_index(name="Piece Count")
                        )
                        summary_volumes = (
                            df_summary.groupby(desc_key)[vol_key]
                            .sum()
                            .reset_index(name="Total Volume")
                        )
                        summary = pd.merge(summary_counts, summary_volumes, on=desc_key)
                        summary = summary.sort_values("Total Volume", ascending=False)
                        st.dataframe(summary, width="stretch", hide_index=True)

                        total_pieces = summary["Piece Count"].sum()
                        total_volume = summary["Total Volume"].sum()
                        st.write(
                            f"**Total pieces: {int(total_pieces)}  |  Total volume: {total_volume:,.3f}**"
                        )
                    else:
                        st.info("No MA-Description values found in user_text")
                else:
                    st.info("No user_text column found in rhino_breps")

        else:
            st.info(f"ℹ️ No BREPs found for project: {selected_project}")
        
        st.markdown("---")
        
        # Connections Section (filtered by selected project)
        st.markdown("### 🔩 Connections Summary")
        
        # Filter Connections data by selected project
        rows = df_blocks_filtered.to_dict('records')
        
        if not rows:
            st.warning("⚠️ Query returned 0 rows")
            st.info("""
            **Possible causes:**
            1. **RLS (Row Level Security)** policies may be blocking access
            2. Table is empty or doesn't exist
            3. Wrong credentials or permissions
            
            **Next steps:**
            - Check Supabase dashboard to verify table has data
            - Check RLS policies on the `rhino_blocks` table
            - Try disabling RLS temporarily for testing
            """)
        else:
            df = pd.DataFrame(rows)

            # Basic stats
            total_rows = len(df)
            latest_batch = df["batch_id"].max() if "batch_id" in df.columns else "N/A"
            total_quantity = df["total_quantity"].sum() if "total_quantity" in df.columns else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", total_rows)
            col2.metric("Latest Batch", str(latest_batch))
            col3.metric("Total Quantity", int(total_quantity))

            tab_qty, tab_prefixes, tab_ref_detail = st.tabs(
                ["Quantities", "Prefixes", "Ref Detail"]
            )

            with tab_qty:
                st.markdown("**Quantity summary by Connection name**")
                if "block_name" in df.columns and "total_quantity" in df.columns:
                    qty_summary = (
                        df.groupby("block_name")["total_quantity"]
                        .sum()
                        .reset_index()
                        .sort_values("total_quantity", ascending=False)
                    )
                    st.dataframe(qty_summary, width="stretch", hide_index=True)
                    st.bar_chart(qty_summary.set_index("block_name").head(20))

            with tab_prefixes:
                st.markdown("**Quantity summary by prefix**")
                if "block_name" in df.columns and "quantity" in df.columns:
                    df["prefix"] = df["block_name"].str.split("_").str[0]
                    prefix_summary = (
                        df.groupby("prefix")
                        .agg(
                            block_count=("block_name", "nunique"),
                            total_qty=("quantity", "sum"),
                        )
                        .reset_index()
                        .sort_values("total_qty", ascending=False)
                    )
                    st.bar_chart(prefix_summary.set_index("prefix").head(20))

                    st.markdown("**Click a prefix to see all instances**")
                    for _, row in prefix_summary.iterrows():
                        prefix = row["prefix"]
                        count = row["block_count"]
                        qty = row["total_qty"]
                        with st.expander(f"**{prefix}** — {count} Connections, total qty: {qty}"):
                            prefix_df = df[df["prefix"] == prefix]
                            block_rollup = (
                                prefix_df.groupby("block_name")
                                .agg(quantity=("quantity", "sum"))
                                .reset_index()
                                .sort_values("quantity", ascending=False)
                            )
                            for _, block_row in block_rollup.iterrows():
                                block_name = block_row["block_name"]
                                block_qty = block_row["quantity"]
                                with st.expander(f"**{block_name}** — qty: {block_qty}"):
                                    instance_df = prefix_df[
                                        prefix_df["block_name"] == block_name
                                    ][["block_name", "quantity", "parent_block"]].sort_values(
                                        "quantity", ascending=False
                                    )
                                    st.dataframe(instance_df, width="stretch", hide_index=True)
                else:
                    st.info("No block_name or quantity column found.")

            with tab_ref_detail:
                st.markdown("**Quantity summary by ref detail**")
                if "blk_ref_detail" in df.columns and "total_quantity" in df.columns:
                    ref_summary = (
                        df.groupby("blk_ref_detail")
                        .agg(
                            block_count=("block_name", "nunique"),
                            total_qty=("total_quantity", "sum"),
                        )
                        .reset_index()
                        .sort_values("total_qty", ascending=False)
                    )
                    st.bar_chart(ref_summary.set_index("blk_ref_detail").head(20))

                    st.markdown("**Click a ref detail to see all instances**")
                    for _, row in ref_summary.iterrows():
                        ref = row["blk_ref_detail"]
                        count = row["block_count"]
                        qty = row["total_qty"]
                        with st.expander(f"**{ref}** — {count} Connections, total qty: {qty}"):
                            ref_df = df[df["blk_ref_detail"] == ref][
                                ["block_name", "quantity", "total_quantity", "parent_block", "prefix"]
                            ].sort_values("total_quantity", ascending=False)
                            st.dataframe(ref_df, width="stretch", hide_index=True)
                else:
                    st.info("No blk_ref_detail or total_quantity column found.")
        
        st.markdown("---")
        
        # ============================================================
        # SECTION 2: PROJECT TASK TRACKING
        # ============================================================
        st.markdown("## 📋 Project Task Tracking")
        st.markdown("---")
        
        # Plan Detail Refs Section (filtered by selected project)
        st.markdown("### � Plan Detail Summary")
        
        try:
            # Fetch plan_detail_refs data
            try:
                plan_detail_refs = supabase.select("plan_detail_refs", limit=10000)
                st.sidebar.info(f"✅ plan_detail_refs: {len(plan_detail_refs)} rows")
            except Exception as plan_error:
                st.sidebar.error(f"❌ plan_detail_refs error: {str(plan_error)}")
                plan_detail_refs = None
            
            if plan_detail_refs and len(plan_detail_refs) > 0:
                df_plan = pd.DataFrame(plan_detail_refs)
                
                # Filter by selected project if project_id column exists
                if "project_id" in df_plan.columns:
                    df_plan_filtered = df_plan[df_plan["project_id"] == selected_project]
                else:
                    df_plan_filtered = df_plan
                
                if not df_plan_filtered.empty and "ref_data" in df_plan_filtered.columns:
                    # Extract data from JSONB column - create separate rows for each prefix found
                    plan_data = []
                    for _, row in df_plan_filtered.iterrows():
                        ref_data = row.get("ref_data", {})
                        if isinstance(ref_data, dict):
                            ref_name = row.get("ref_name", "")
                            
                            # Check for TN_ fields and create a TN row if found
                            if "TN_Owner" in ref_data or "TN_Status" in ref_data or "TN_progress" in ref_data:
                                plan_data.append({
                                    "ref_name": ref_name,
                                    "prefix": "TN",
                                    "owner": ref_data.get("TN_Owner", ""),
                                    "status": ref_data.get("TN_Status", ""),
                                    "progress": ref_data.get("TN_progress", 0),
                                    "asm_model_status": "",
                                    "asm_2d_status": "",
                                    "hardware_status": ""
                                })
                            
                            # Check for ASM_ fields and create an ASM row if found
                            if "2D_Owner" in ref_data or "ASM_Model_Status" in ref_data or "ASM_2D_Status" in ref_data or "ASM_2D_Progress" in ref_data:
                                plan_data.append({
                                    "ref_name": ref_name,
                                    "prefix": "ASM",
                                    "owner": ref_data.get("2D_Owner", ""),
                                    "status": ref_data.get("ASM_2D_Status", ""),
                                    "progress": 0,
                                    "asm_model_status": ref_data.get("ASM_Model_Status", ""),
                                    "asm_2d_status": ref_data.get("ASM_2D_Status", ""),
                                    "hardware_status": ""
                                })
                            
                            # Check for FA_ fields and create an FA row if found
                            if "FA_Owner" in ref_data or "FA_progress" in ref_data or "FA_Status" in ref_data:
                                plan_data.append({
                                    "ref_name": ref_name,
                                    "prefix": "FA",
                                    "owner": ref_data.get("FA_Owner", ""),
                                    "status": ref_data.get("FA_Status", ""),
                                    "progress": ref_data.get("FA_progress", 0),
                                    "asm_model_status": "",
                                    "asm_2d_status": "",
                                    "hardware_status": ""
                                })
                            
                            # Check for Hardware_ fields and create a Hardware row if found
                            if "Hardware_Status" in ref_data or "Hardware_progress" in ref_data:
                                plan_data.append({
                                    "ref_name": ref_name,
                                    "prefix": "Hardware",
                                    "owner": "",
                                    "status": ref_data.get("Hardware_Status", ""),
                                    "progress": 0,
                                    "asm_model_status": "",
                                    "asm_2d_status": "",
                                    "hardware_status": ref_data.get("Hardware_Status", "")
                                })
                    
                    if plan_data:
                        df_summary = pd.DataFrame(plan_data)
                        
                        # Debug: Show prefix distribution
                        prefix_debug = df_summary["prefix"].value_counts().to_dict()
                        st.sidebar.info(f"📊 Prefix counts: {prefix_debug}")
                        
                        # Create summary tabs by prefix
                        tab_overview, tab_tn, tab_asm, tab_hardware, tab_fa = st.tabs(
                            ["Overview", "TN_", "ASM_", "Hardware_", "FA_"]
                        )
                        
                        with tab_overview:
                            st.markdown("**Summary by Prefix**")
                            
                            # Count by prefix
                            prefix_counts = df_summary["prefix"].value_counts().reset_index()
                            prefix_counts.columns = ["Prefix", "Count"]
                            
                            col1, col2, col3, col4, col5 = st.columns(5)
                            for idx, (prefix, count) in enumerate(zip(prefix_counts["Prefix"], prefix_counts["Count"])):
                                cols = [col1, col2, col3, col4, col5]
                                cols[idx % 5].metric(f"{prefix}", count)
                            
                            # Status distribution
                            st.markdown("**Status Distribution**")
                            status_counts = df_summary[df_summary["status"] != ""]["status"].value_counts().reset_index()
                            status_counts.columns = ["Status", "Count"]
                            if not status_counts.empty:
                                st.bar_chart(status_counts.set_index("Status"))
                            
                            # Owner distribution
                            st.markdown("**Owner Distribution**")
                            owner_counts = df_summary[df_summary["owner"] != ""]["owner"].value_counts().reset_index()
                            owner_counts.columns = ["Owner", "Count"]
                            if not owner_counts.empty:
                                st.dataframe(owner_counts, hide_index=True)
                        
                        with tab_tn:
                            st.markdown("**TN_ Items**")
                            df_tn = df_summary[df_summary["prefix"] == "TN"]
                            if not df_tn.empty:
                                st.metric("Total TN Items", len(df_tn))
                                
                                # Progress summary
                                avg_progress = df_tn["progress"].mean() if df_tn["progress"].notna().any() else 0
                                st.metric("Average Progress", f"{avg_progress:.1f}%")
                                
                                # Group by owner and status
                                if df_tn["owner"].notna().any():
                                    st.markdown("**By Owner**")
                                    owner_summary = df_tn.groupby("owner").agg({
                                        "ref_name": "count",
                                        "progress": "mean"
                                    }).reset_index()
                                    owner_summary.columns = ["Owner", "Count", "Avg Progress"]
                                    owner_summary["Avg Progress"] = owner_summary["Avg Progress"].round(1)
                                    st.dataframe(owner_summary, hide_index=True)
                                
                                if df_tn["status"].notna().any():
                                    st.markdown("**By Status**")
                                    status_summary = df_tn[df_tn["status"] != ""].groupby("status").size().reset_index()
                                    status_summary.columns = ["Status", "Count"]
                                    st.dataframe(status_summary, hide_index=True)
                                
                                with st.expander("View All TN Items"):
                                    st.dataframe(df_tn[["ref_name", "owner", "status", "progress"]], hide_index=True)
                            else:
                                st.info("No TN_ items found")
                        
                        with tab_asm:
                            st.markdown("**ASM_ Items**")
                            df_asm = df_summary[df_summary["prefix"] == "ASM"]
                            if not df_asm.empty:
                                st.metric("Total ASM Items", len(df_asm))
                                
                                # Model status summary
                                if df_asm["asm_model_status"].notna().any():
                                    st.markdown("**Model Status**")
                                    model_status = df_asm[df_asm["asm_model_status"] != ""]["asm_model_status"].value_counts().reset_index()
                                    model_status.columns = ["Status", "Count"]
                                    st.dataframe(model_status, hide_index=True)
                                
                                # 2D status summary
                                if df_asm["asm_2d_status"].notna().any():
                                    st.markdown("**2D Status**")
                                    status_2d = df_asm[df_asm["asm_2d_status"] != ""]["asm_2d_status"].value_counts().reset_index()
                                    status_2d.columns = ["Status", "Count"]
                                    st.dataframe(status_2d, hide_index=True)
                                
                                # Group by owner
                                if df_asm["owner"].notna().any():
                                    st.markdown("**By Owner**")
                                    owner_summary = df_asm[df_asm["owner"] != ""].groupby("owner").size().reset_index()
                                    owner_summary.columns = ["Owner", "Count"]
                                    st.dataframe(owner_summary, hide_index=True)
                                
                                with st.expander("View All ASM Items"):
                                    st.dataframe(df_asm[["ref_name", "owner", "asm_model_status", "asm_2d_status"]], hide_index=True)
                            else:
                                st.info("No ASM_ items found")
                        
                        with tab_hardware:
                            st.markdown("**Hardware_ Items**")
                            df_hw = df_summary[df_summary["prefix"] == "Hardware"]
                            if not df_hw.empty:
                                st.metric("Total Hardware Items", len(df_hw))
                                
                                # Hardware status summary
                                if df_hw["hardware_status"].notna().any():
                                    st.markdown("**Hardware Status**")
                                    hw_status = df_hw[df_hw["hardware_status"] != ""]["hardware_status"].value_counts().reset_index()
                                    hw_status.columns = ["Status", "Count"]
                                    st.dataframe(hw_status, hide_index=True)
                                
                                with st.expander("View All Hardware Items"):
                                    st.dataframe(df_hw[["ref_name", "hardware_status"]], hide_index=True)
                            else:
                                st.info("No Hardware_ items found")
                        
                        with tab_fa:
                            st.markdown("**FA_ Items**")
                            df_fa = df_summary[df_summary["prefix"] == "FA"]
                            if not df_fa.empty:
                                st.metric("Total FA Items", len(df_fa))
                                
                                # Progress summary
                                avg_progress = df_fa["progress"].mean() if df_fa["progress"].notna().any() else 0
                                st.metric("Average Progress", f"{avg_progress:.1f}%")
                                
                                # Group by status
                                if df_fa["status"].notna().any():
                                    st.markdown("**By Status**")
                                    status_summary = df_fa[df_fa["status"] != ""].groupby("status").size().reset_index()
                                    status_summary.columns = ["Status", "Count"]
                                    st.dataframe(status_summary, hide_index=True)
                                
                                with st.expander("View All FA Items"):
                                    st.dataframe(df_fa[["ref_name", "status", "progress"]], hide_index=True)
                            else:
                                st.info("No FA_ items found")
                    else:
                        st.info("No valid plan detail data found")
                else:
                    st.info(f"ℹ️ No plan details found for project: {selected_project}")
            else:
                st.info("ℹ️ No data in plan_detail_refs table")
        except Exception as e:
            st.warning(f"⚠️ Could not load plan detail data: {str(e)}")
        
        st.markdown("---")
        
        # Plan Detail Summary by Owner Section
        st.markdown("### 👤 Plan Detail Summary by Owner")
        
        try:
            # Reuse the plan_detail_refs data if available
            if plan_detail_refs and len(plan_detail_refs) > 0:
                df_plan = pd.DataFrame(plan_detail_refs)
                
                # Filter by selected project if project_id column exists
                if "project_id" in df_plan.columns:
                    df_plan_filtered = df_plan[df_plan["project_id"] == selected_project]
                else:
                    df_plan_filtered = df_plan
                
                if not df_plan_filtered.empty and "ref_data" in df_plan_filtered.columns:
                    # Extract owner data from JSONB
                    owner_data = []
                    for _, row in df_plan_filtered.iterrows():
                        ref_data = row.get("ref_data", {})
                        if isinstance(ref_data, dict):
                            ref_name = row.get("ref_name", "")
                            
                            # Extract all owner fields
                            tn_owner = ref_data.get("TN_Owner", "")
                            asm_owner = ref_data.get("2D_Owner", "")
                            fa_owner = ref_data.get("FA_Owner", "")
                            
                            # Add TN owner entry
                            if tn_owner:
                                owner_data.append({
                                    "owner": tn_owner,
                                    "ref_name": ref_name,
                                    "category": "TN",
                                    "status": ref_data.get("TN_Status", ""),
                                    "progress": ref_data.get("TN_progress", 0)
                                })
                            
                            # Add ASM owner entry
                            if asm_owner:
                                owner_data.append({
                                    "owner": asm_owner,
                                    "ref_name": ref_name,
                                    "category": "ASM",
                                    "status": ref_data.get("ASM_2D_Status", ""),
                                    "progress": 0
                                })
                            
                            # Add FA owner entry
                            if fa_owner:
                                owner_data.append({
                                    "owner": fa_owner,
                                    "ref_name": ref_name,
                                    "category": "FA",
                                    "status": ref_data.get("FA_Status", ""),
                                    "progress": ref_data.get("FA_progress", 0)
                                })
                    
                    if owner_data:
                        df_owners = pd.DataFrame(owner_data)
                        
                        # Get unique owners
                        unique_owners = sorted(df_owners["owner"].unique())
                        
                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Owners", len(unique_owners))
                        col2.metric("Total Assignments", len(df_owners))
                        avg_progress = df_owners[df_owners["progress"] > 0]["progress"].mean()
                        col3.metric("Avg Progress", f"{avg_progress:.1f}%" if not pd.isna(avg_progress) else "N/A")
                        
                        # Owner summary table
                        st.markdown("**Summary by Owner**")
                        owner_summary = df_owners.groupby("owner").agg({
                            "ref_name": "count",
                            "progress": lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0
                        }).reset_index()
                        owner_summary.columns = ["Owner", "Total Items", "Avg Progress"]
                        owner_summary["Avg Progress"] = owner_summary["Avg Progress"].round(1)
                        owner_summary = owner_summary.sort_values("Total Items", ascending=False)
                        st.dataframe(owner_summary, hide_index=True)
                        
                        # Detailed breakdown by owner
                        st.markdown("**Detailed Breakdown by Owner**")
                        for owner in unique_owners:
                            owner_df = df_owners[df_owners["owner"] == owner]
                            total_items = len(owner_df)
                            
                            # Category breakdown
                            category_counts = owner_df["category"].value_counts().to_dict()
                            category_str = ", ".join([f"{cat}: {count}" for cat, count in category_counts.items()])
                            
                            with st.expander(f"**{owner}** — {total_items} items ({category_str})"):
                                # Show items by category
                                for category in ["TN", "ASM", "FA"]:
                                    cat_df = owner_df[owner_df["category"] == category]
                                    if not cat_df.empty:
                                        st.markdown(f"**{category} Items ({len(cat_df)})**")
                                        display_df = cat_df[["ref_name", "status", "progress"]].copy()
                                        display_df = display_df.sort_values("progress", ascending=False)
                                        st.dataframe(display_df, hide_index=True)
                    else:
                        st.info("No owner data found")
                else:
                    st.info(f"ℹ️ No plan details found for project: {selected_project}")
            else:
                st.info("ℹ️ No data in plan_detail_refs table")
        except Exception as e:
            st.warning(f"⚠️ Could not load owner summary: {str(e)}")
        
        # Consolidated Debug Section (at bottom)
        st.markdown("---")
        with st.expander("🔍 Debug Information", expanded=False):
            st.markdown("#### Project Data")
            st.write(f"**Projects from project_data table:** {project_ids}")
            st.write(f"**Total projects:** {len(project_ids)}")
            
            st.markdown("#### Current Selection")
            st.write(f"**Selected Project:** {selected_project}")
            st.write(f"**Connections for this project:** {len(rows)}")
            st.write(f"**BREPs for this project:** {len(df_breps_filtered)}")
            
            st.markdown("#### Connection")
            st.write(f"**Supabase URL:** {supabase_url}")
            
            st.markdown("#### Sample Connection Data")
            if rows:
                st.json(rows[:2])
            
            st.markdown("#### Plan Detail Refs Data")
            try:
                plan_debug = supabase.select("plan_detail_refs", limit=5)
                st.write(f"**Total rows fetched:** {len(plan_debug) if plan_debug else 0}")
                if plan_debug:
                    st.write(f"**Sample columns:** {list(plan_debug[0].keys()) if plan_debug else 'N/A'}")
                    
                    # Show JSONB keys from each record
                    st.markdown("**JSONB Keys in each record:**")
                    for i, record in enumerate(plan_debug[:3]):
                        ref_data = record.get("ref_data", {})
                        if isinstance(ref_data, dict):
                            st.write(f"Record {i+1} ({record.get('ref_name', 'unknown')}): {list(ref_data.keys())}")
                    
                    st.json(plan_debug[:2])
            except Exception as e:
                st.error(f"Error fetching plan_detail_refs: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error fetching Connection data: {str(e)}")
        with st.expander("🐛 Full Error Details"):
            import traceback
            st.code(traceback.format_exc())

#
# To test this app locally:
#   cd "C:\Users\Dan\Documents\GitHub\Metrics\supabase-project-dashboard"
#   python -m streamlit run app.py
#

