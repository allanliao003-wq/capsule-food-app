import streamlit as st
import google.generativeai as genai
import json

# 1. 網頁基本設定
st.set_page_config(page_title="膠囊食品開發評估", page_icon="💊")
st.title("💊 膠囊食品研發與法規評估系統")
st.markdown("輸入你的產品構想，AI [配方工程師] 與 [法規專家] 將自動為您進行雙重評估。")

# 2. 側邊欄：讓用戶輸入 Gemini API Key
with st.sidebar:
    st.header("⚙️ 系統設定")
    api_key = st.text_input("請輸入您的 Gemini API Key", type="password")
    st.markdown("[👉 點此免費取得 API Key](https://aistudio.google.com/app/apikey)")

# 3. 主畫面：用戶輸入區
product_idea = st.text_area(
    "請描述你想開發的膠囊食品：", 
    placeholder="例如：添加高濃度葉黃素、魚油與黑瑪卡，主打天天熬夜的工程師，每日兩顆。"
)

# 4. 核心工作流：當按下按鈕後執行
if st.button("🚀 開始智能評估 (工程師 -> 法務)"):
    if not api_key:
        st.error("請先在左側輸入 Gemini API Key！")
    elif not product_idea:
        st.warning("請填寫產品構想！")
    else:
        with st.spinner("AI 專家團隊正在瘋狂運算中，請稍候..."):
            try:
                # 設定 API
                genai.configure(api_key=api_key)
                
                # 設定 System Prompt (鎖定 JSON 與多代理人流程)
                model = genai.GenerativeModel(
                    "gemini-1.5-flash",
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.2
                    },
                    system_instruction="""
                    你是一個膠囊食品公司的自動化工作流引擎。請嚴格按照以下順序處理用戶的新產品開發需求，不允許任何口語解釋。
                    
                    工作流程：
                    1. [配方工程師]：分析配方相容性、製程難點與潛在風險。
                    2. [食安法規專家]：根據台灣食品安全法規，評估上述成分是否合法、以及包裝標示注意事項。
                    
                    輸出規範：請直接輸出符合以下格式的 JSON：
                    {
                      "engineer": {
                        "feasibility": "可行 / 需調整 / 困難",
                        "tech_analysis": "配方的相容性與製程分析說明",
                        "risks": ["風險1", "風險2"]
                      },
                      "legal": {
                        "status": "合法 / 需警語 / 違法",
                        "advice": "法規建議與標示注意"
                      }
                    }
                    """
                )
                
                # 呼叫 API 並解析結果
                response = model.generate_content(product_idea)
                result = json.loads(response.text)
                
                # 5. 漂亮地呈現在網頁上
                st.success("評估完成！請查看以下報告：")
                
                st.subheader("👨‍🔬 配方工程師分析報告")
                st.info(f"**技術可行性：** {result['engineer']['feasibility']}")
                st.write(f"**分析說明：** {result['engineer']['tech_analysis']}")
                st.write("**⚠️ 潛在風險：**")
                for r in result['engineer']['risks']:
                    st.markdown(f"- {r}")
                    
                st.markdown("---")
                
                st.subheader("⚖️ 食安法規專家評估")
                if result['legal']['status'] == "違法":
                    st.error(f"**合規狀態：** {result['legal']['status']}")
                else:
                    st.warning(f"**合規狀態：** {result['legal']['status']}")
                st.write(f"**法規與標示建議：** {result['legal']['advice']}")
                
            except Exception as e:
                st.error(f"系統發生錯誤，請檢查 API Key 或稍後再試。錯誤細節：{e}")
