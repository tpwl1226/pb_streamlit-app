import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="MASTER PB 조색 계산기", layout="centered")

st.title("🎨 MASTER PB 조색 계산기")
st.markdown("사용자의 조색값을 기반으로 추천 PB 및 XFINE 투입량을 계산합니다.")

# 1. 사용자 입력
with st.form("target_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        inno_tio2 = st.number_input("INNO TIO2 (%)", value=None, format="%.2f")
        ioy = st.number_input("IOY (%)", value=None, format="%.2f")
        xf_ioy = st.number_input("XFINE IOY (%)", value=None, format="%.2f")
    with col2:
        cmj = st.number_input("CMJ (%)", value=None, format="%.2f")
        ior = st.number_input("IOR (%)", value=None, format="%.2f")
        xf_ior = st.number_input("XFINE IOR (%)", value=None, format="%.2f")
    with col3:
        pb_usage = st.number_input("PB 사용량 (%)", value=None, format="%.2f")
        iob = st.number_input("IOB (%)", value=None, format="%.2f")
        xf_iob = st.number_input("XFINE IOB (%)", value=None, format="%.2f")

    submitted = st.form_submit_button("계산하기")

# 2. 계산 로직 실행
if submitted:
    try:
        target = {
            "INNO_TIO2": inno_tio2,
            "CMJ": cmj,
            "IOY": ioy,
            "IOR": ior,
            "IOB": iob,
            "PB_Usage": pb_usage,
            "XFINE_IOY": xf_ioy,
            "XFINE_IOR": xf_ior,
            "XFINE_IOB": xf_iob
        }

        # PB 데이터
        pb_data = [
            {"PB": 0, "PB_Percent": 18, "INNO_TIO2": 38.89, "CMJ": 44.44, "IOY": 0, "IOR": 0, "IOB": 0},
            {"PB": 1, "PB_Percent": 19, "INNO_TIO2": 36.84, "CMJ": 42.11, "IOY": 10.65, "IOR": 2.55, "IOB": 0.92},
            {"PB": 2, "PB_Percent": 20, "INNO_TIO2": 35.00, "CMJ": 30.00, "IOY": 19.89, "IOR": 2.37, "IOB": 1.72},
            {"PB": 3, "PB_Percent": 20, "INNO_TIO2": 35.00, "CMJ": 20.00, "IOY": 26.45, "IOR": 3.99, "IOB": 2.92},
            {"PB": 4, "PB_Percent": 20, "INNO_TIO2": 35.00, "CMJ": 10.00, "IOY": 27.76, "IOR": 5.00, "IOB": 3.82},
            {"PB": 5, "PB_Percent": 20, "INNO_TIO2": 35.00, "CMJ": 2.50, "IOY": 21.71, "IOR": 7.63, "IOB": 5.60},
            {"PB": 6, "PB_Percent": 22, "INNO_TIO2": 31.82, "CMJ": 0.91, "IOY": 14.29, "IOR": 8.50, "IOB": 6.40},
            {"PB": 7, "PB_Percent": 22, "INNO_TIO2": 31.82, "CMJ": 0.91, "IOY": 6.72, "IOR": 13.27, "IOB": 11.41},
            {"PB": 8, "PB_Percent": 22, "INNO_TIO2": 0.00, "CMJ": 0.00, "IOY": 21.50, "IOR": 23.00, "IOB": 29.00},
            {"PB": 9, "PB_Percent": 20, "INNO_TIO2": 0.00, "CMJ": 0.00, "IOY": 18.04, "IOR": 11.84, "IOB": 39.43},
        ]
        pb_df = pd.DataFrame(pb_data)

        # 유효성 확인
        inno_total = target["INNO_TIO2"] * target["PB_Usage"] / 100
        if inno_total < 7:
            st.warning(f"⚠️ 주성분 함량이 다릅니다. ({inno_total:.2f}%)")

        # PB 0 먼저 계산
        if target["IOY"] == 0 and target["IOR"] == 0 and target["IOB"] == 0:
            pb0 = pb_df[pb_df["PB"] == 0].iloc[0]
            cmj_pb0_whole = pb0["CMJ"] * 0.18
            cmj_diff = cmj_pb0_whole - target["CMJ"] * target["PB_Usage"] / 100 
            colorant_boost = 1 + (cmj_diff * 0.07)

            xf_ioy = target["XFINE_IOY"] * colorant_boost
            xf_ior = target["XFINE_IOR"] * colorant_boost
            xf_iob = target["XFINE_IOB"] * colorant_boost
            total_xfine = xf_ioy + xf_ior + xf_iob

            st.success("✅ PB 후보 1: PB 0 + XFINE")
            st.markdown(f"📊 CMJ 차이: **{cmj_diff:.2f}%p** (처방 기준)")
            st.markdown("📈 XFINE 추가 투입량 (보정 후):")
            st.markdown(f" - XFINE IOY: **{xf_ioy:.2f}%**")
            st.markdown(f" - XFINE IOR: **{xf_ior:.2f}%**")
            st.markdown(f" - XFINE IOB: **{xf_iob:.2f}%**")
            st.markdown(f"🔷 **TOTAL XFINE 투입량: {total_xfine:.2f}%**")

        # 다른 PB 조합 계산
        def compute_adjusted_colorants(row):
            scale = target["PB_Usage"] / row["PB_Percent"]
            if pd.isnull(row["CMJ"]):
                return pd.Series([None]*9, index=[
                    "Adj_CMJ", "CMJ_Diff", "Colorant_Scale",
                    "Adj_IOY", "Adj_IOR", "Adj_IOB",
                    "Total_Colorant", "Eligible", "PB"
                ])
            adj_cmj = row["CMJ"] * row["PB_Percent"] / 100
            cmj_diff = target["CMJ"] * target["PB_Usage"] / 100 - adj_cmj
            colorant_scale = 1 + (cmj_diff * 0.07)

            adj_ioy = row["IOY"] * scale * colorant_scale + target["XFINE_IOY"] * 0.5
            adj_ior = row["IOR"] * scale * colorant_scale + target["XFINE_IOR"] * 0.45
            adj_iob = row["IOB"] * scale * colorant_scale + target["XFINE_IOB"] * 0.6
            total_colorant = adj_ioy + adj_ior + adj_iob

            eligible = (
                adj_ioy * row["PB_Percent"] / 100 < target["IOY"] * target["PB_Usage"] / 100 and
                adj_ior * row["PB_Percent"] / 100 < target["IOR"] * target["PB_Usage"] / 100 and
                adj_iob * row["PB_Percent"] / 100 < target["IOB"] * target["PB_Usage"] / 100
            )

            return pd.Series([
                adj_cmj, cmj_diff, colorant_scale,
                adj_ioy, adj_ior, adj_iob,
                total_colorant, eligible, row["PB"]
            ], index=[
                "Adj_CMJ", "CMJ_Diff", "Colorant_Scale",
                "Adj_IOY", "Adj_IOR", "Adj_IOB",
                "Total_Colorant", "Eligible", "PB"
            ])

        results = pb_df.apply(compute_adjusted_colorants, axis=1)
        eligible_df = results[results["Eligible"] == True]

        if not eligible_df.empty:
            best_pb = eligible_df.sort_values("Total_Colorant", ascending=False).iloc[0]
            pb_percent = pb_df.loc[pb_df["PB"] == best_pb["PB"], "PB_Percent"].values[0]

            short_ioy = target["IOY"] * target["PB_Usage"] / 100 - best_pb["Adj_IOY"] * pb_percent / 100
            short_ior = target["IOR"] * target["PB_Usage"] / 100 - best_pb["Adj_IOR"] * pb_percent / 100
            short_iob = target["IOB"] * target["PB_Usage"] / 100 - best_pb["Adj_IOB"] * pb_percent / 100

            xf_ioy = short_ioy / 0.40
            xf_ior = short_ior / 0.45
            xf_iob = short_iob / 0.75
            total_xfine = xf_ioy + xf_ior + xf_iob

            st.success(f"✅ PB 후보 2: PB {int(best_pb['PB'])} + XFINE")
            st.markdown("📉 부족한 색소량 (전체 처방 기준):")
            st.markdown(f" - XFINE IOY 추가 투입량 : **{xf_ioy:.2f}%**")
            st.markdown(f" - XFINE IOR 추가 투입량 : **{xf_ior:.2f}%**")
            st.markdown(f" - XFINE IOB 추가 투입량 : **{xf_iob:.2f}%**")
            st.markdown(f"🔷 **TOTAL XFINE 투입량 : {total_xfine:.2f}%**")
        else:
            st.error("❌ 추천 가능한 PB 후보가 없습니다.")
    except Exception as e:
        st.error(f"에러 발생: {e}")
