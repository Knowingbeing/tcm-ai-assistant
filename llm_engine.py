import os
from typing import List, Dict

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

API_PROVIDERS = {
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
        "default_model": "gpt-3.5-turbo",
        "key_prefix": "sk-",
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-chat", "deepseek-coder"],
        "default_model": "deepseek-chat",
        "key_prefix": "sk-",
    },
    "MiMo (小米)": {
        "base_url": "https://token-plan-cn.xiaomimimo.com/v1",
        "models": ["mimo-auto", "mimo-pro"],
        "default_model": "mimo-auto",
        "key_prefix": "sk-",
    },
    "硅基流动 (SiliconFlow)": {
        "base_url": "https://api.siliconflow.cn/v1",
        "models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-V3", "THUDM/glm-4-9b-chat"],
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
        "key_prefix": "sk-",
    },
    "通义千问 (阿里)": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
        "default_model": "qwen-turbo",
        "key_prefix": "sk-",
    },
    "智谱AI (GLM)": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-flash", "glm-4", "glm-4-plus"],
        "default_model": "glm-4-flash",
        "key_prefix": "",
    },
    "Moonshot (Kimi)": {
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "default_model": "moonshot-v1-8k",
        "key_prefix": "sk-",
    },
}

class TCMDiagnosisEngine:
    def __init__(self, api_key: str = "", provider: str = "OpenAI", model: str = ""):
        self.provider = provider
        provider_config = API_PROVIDERS.get(provider, API_PROVIDERS["OpenAI"])

        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY", "")

        self.has_api_key = bool(api_key) and len(api_key) > 5

        if self.has_api_key:
            try:
                if OpenAI is None:
                    raise ImportError("openai package not installed")
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=provider_config["base_url"]
                )
                self.model = model or provider_config["default_model"]
            except Exception:
                self.has_api_key = False
        else:
            self.model = ""

        self.knowledge_base = self._load_knowledge_base()

    def _rule_based_diagnosis(self, chief_complaint: str, symptoms: List[str],
                              tongue_sign: str, pulse_sign: str) -> Dict:
        all_text = chief_complaint + " " + " ".join(symptoms) + " " + tongue_sign + " " + pulse_sign

        if any(w in all_text for w in ["恶寒", "无汗", "鼻塞", "流清涕", "头身疼痛", "头痛", "身痛"]):
            return {"syndrome": "太阳伤寒证", "syndrome_category": "六经辨证",
                    "analysis": "患者恶寒、无汗、鼻塞流清涕、头身疼痛，为风寒之邪侵袭太阳经，卫阳被遏，营阴郁滞。",
                    "formula": "麻黄汤", "formula_adjustment": "若鼻塞重可加辛夷、苍耳子；若咳嗽加杏仁",
                    "treatment_principle": "发汗解表、宣肺平喘", "confidence": 80,
                    "additional_notes": "演示模式：服药后温覆取微汗，忌食生冷。"}
        elif any(w in all_text for w in ["发热", "汗出", "恶风"]):
            return {"syndrome": "太阳中风证", "syndrome_category": "六经辨证",
                    "analysis": "患者发热汗出、恶风，为风邪袭表，营卫不和。",
                    "formula": "桂枝汤", "formula_adjustment": "若项背强可加葛根；若鼻塞加辛夷",
                    "treatment_principle": "解肌发表、调和营卫", "confidence": 80,
                    "additional_notes": "演示模式：服后啜热稀粥以助药力。"}
        elif any(w in all_text for w in ["咽喉痛", "咽痛", "发热", "微恶风寒", "口渴"]):
            return {"syndrome": "风热感冒", "syndrome_category": "卫气营血辨证",
                    "analysis": "患者发热微恶风寒、咽喉肿痛、口渴，为风热之邪侵袭肺卫。",
                    "formula": "银翘散", "formula_adjustment": "若咳嗽加杏仁；若口渴甚加天花粉",
                    "treatment_principle": "辛凉解表、清热解毒", "confidence": 80,
                    "additional_notes": "演示模式：忌食辛辣油腻。"}
        elif any(w in all_text for w in ["口苦", "咽干", "往来寒热", "胸胁苦满", "心烦喜呕"]):
            return {"syndrome": "少阳病证", "syndrome_category": "六经辨证",
                    "analysis": "患者口苦咽干、往来寒热、胸胁苦满，为邪犯少阳胆经，枢机不利。",
                    "formula": "小柴胡汤", "formula_adjustment": "若口渴去半夏加天花粉；若腹痛加白芍",
                    "treatment_principle": "和解少阳", "confidence": 85,
                    "additional_notes": "演示模式：忌食油腻辛辣。"}
        elif any(w in all_text for w in ["身大热", "汗大出", "口大渴", "大热", "大汗", "大渴"]):
            return {"syndrome": "阳明经证", "syndrome_category": "六经辨证",
                    "analysis": "患者身热、大汗、大渴，为邪热亢盛，充斥内外。",
                    "formula": "白虎汤", "formula_adjustment": "若气虚可加人参；若高热不退加石膏",
                    "treatment_principle": "清热生津", "confidence": 85,
                    "additional_notes": "演示模式：高热期间注意物理降温，多饮水。"}
        elif any(w in all_text for w in ["便秘", "腹胀", "腹痛", "潮热", "谵语"]):
            return {"syndrome": "阳明腑实证", "syndrome_category": "六经辨证",
                    "analysis": "患者便秘、腹胀满硬痛、潮热，为邪热与肠中糟粕互结。",
                    "formula": "大承气汤", "formula_adjustment": "若体虚可去芒硝用小承气汤",
                    "treatment_principle": "峻下热结", "confidence": 80,
                    "additional_notes": "演示模式：中病即止，不宜久服。"}
        elif any(w in all_text for w in ["胸胁胀痛", "善太息", "情志抑郁", "脉弦", "胁痛"]):
            return {"syndrome": "肝气郁结证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者胸胁胀痛、善太息、情志抑郁，为肝失疏泄，气机郁滞。",
                    "formula": "逍遥散", "formula_adjustment": "若肝郁化火可加丹皮、栀子；若胁痛甚加郁金",
                    "treatment_principle": "疏肝解郁、养血健脾", "confidence": 80,
                    "additional_notes": "演示模式：保持心情舒畅，适当运动。"}
        elif any(w in all_text for w in ["头痛", "眩晕", "面红目赤", "急躁易怒", "口苦", "血压高"]):
            return {"syndrome": "肝阳上亢证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者眩晕头痛、面红目赤、急躁易怒，为阴不制阳，肝阳上扰。",
                    "formula": "天麻钩藤饮", "formula_adjustment": "若头痛甚加川芎；若失眠加酸枣仁",
                    "treatment_principle": "滋阴潜阳、平肝息风", "confidence": 80,
                    "additional_notes": "演示模式：忌食辛辣，保持情绪稳定。"}
        elif any(w in all_text for w in ["心悸", "失眠", "多梦", "健忘", "面色萎黄"]):
            return {"syndrome": "心脾两虚证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者心悸失眠、多梦健忘、面色萎黄，为心血不足，脾气虚弱。",
                    "formula": "归脾汤", "formula_adjustment": "若心血虚重可加柏子仁；若纳差加神曲",
                    "treatment_principle": "益气补血、健脾养心", "confidence": 80,
                    "additional_notes": "演示模式：规律作息，避免过度劳累。"}
        elif any(w in all_text for w in ["心烦", "失眠", "口舌生疮", "小便短赤"]):
            return {"syndrome": "心火亢盛证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者心烦失眠、口舌生疮、小便短赤，为心火内炽。",
                    "formula": "导赤散", "formula_adjustment": "若口疮甚加黄连；若尿赤加竹叶",
                    "treatment_principle": "清心泻火", "confidence": 80,
                    "additional_notes": "演示模式：忌食辛辣，多饮水。"}
        elif any(w in all_text for w in ["乏力", "气短", "自汗", "食少", "便溏", "腹胀"]):
            return {"syndrome": "脾气虚证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者乏力、气短、自汗、食少便溏，为脾气不足，运化失健。",
                    "formula": "四君子汤", "formula_adjustment": "若腹胀可加陈皮；若腹泻加山药、扁豆",
                    "treatment_principle": "健脾益气", "confidence": 80,
                    "additional_notes": "演示模式：饮食宜清淡，少食多餐。"}
        elif any(w in all_text for w in ["畏寒", "腹痛", "喜温喜按", "呕吐", "大便稀"]):
            return {"syndrome": "脾阳虚证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者畏寒腹痛、喜温喜按、呕吐便溏，为脾阳不足，虚寒内生。",
                    "formula": "理中丸", "formula_adjustment": "若呕吐加半夏；若腹泻甚加附子",
                    "treatment_principle": "温中健脾", "confidence": 80,
                    "additional_notes": "演示模式：忌食生冷，腹部保暖。"}
        elif any(w in all_text for w in ["咳嗽", "痰多", "胸闷"]):
            if any(w in all_text for w in ["痰黄", "痰稠", "口渴", "发热"]):
                return {"syndrome": "痰热壅肺证", "syndrome_category": "脏腑辨证",
                        "analysis": "患者咳嗽、痰多黄稠、胸闷、口渴，为痰热互结，壅阻于肺。",
                        "formula": "清气化痰丸", "formula_adjustment": "若喘甚加麻黄；若便秘加大黄",
                        "treatment_principle": "清热化痰、宣肺平喘", "confidence": 80,
                        "additional_notes": "演示模式：忌食辛辣油腻，戒烟酒。"}
            else:
                return {"syndrome": "痰湿蕴肺证", "syndrome_category": "脏腑辨证",
                        "analysis": "患者咳嗽痰多、胸闷，为痰湿内停，阻滞气机。",
                        "formula": "二陈汤", "formula_adjustment": "若咳喘可加杏仁、苏子；若痰多加浙贝母",
                        "treatment_principle": "燥湿化痰、理气和中", "confidence": 75,
                        "additional_notes": "演示模式：忌食肥甘厚味，戒烟酒。"}
        elif any(w in all_text for w in ["干咳", "少痰", "潮热", "盗汗"]):
            return {"syndrome": "肺阴虚证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者干咳少痰、潮热盗汗，为肺阴不足，虚热内生。",
                    "formula": "百合固金汤", "formula_adjustment": "若咯血加白及；若潮热甚加地骨皮",
                    "treatment_principle": "滋阴润肺", "confidence": 80,
                    "additional_notes": "演示模式：忌食辛辣，适当休息。"}
        elif any(w in all_text for w in ["畏寒", "肢冷", "腰膝酸软", "阳痿", "夜尿多", "腰痛"]):
            return {"syndrome": "肾阳虚证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者畏寒肢冷、腰膝酸软、夜尿多，为肾阳不足，温煦功能减退。",
                    "formula": "金匮肾气丸", "formula_adjustment": "若阳虚重可加鹿茸；若腰痛甚加杜仲",
                    "treatment_principle": "温补肾阳", "confidence": 80,
                    "additional_notes": "演示模式：避免熬夜，节制房事。"}
        elif any(w in all_text for w in ["腰膝酸软", "头晕", "耳鸣", "潮热", "盗汗", "五心烦热"]):
            return {"syndrome": "肾阴虚证", "syndrome_category": "脏腑辨证",
                    "analysis": "患者腰膝酸软、头晕耳鸣、潮热盗汗，为肾阴亏虚，虚热内生。",
                    "formula": "六味地黄丸", "formula_adjustment": "若盗汗甚加五味子；若头晕加天麻",
                    "treatment_principle": "滋补肾阴", "confidence": 80,
                    "additional_notes": "演示模式：忌食辛辣，避免熬夜。"}
        elif any(w in all_text for w in ["疼痛", "刺痛", "固定", "面色晦暗", "舌紫暗"]):
            return {"syndrome": "血瘀证", "syndrome_category": "气血津液辨证",
                    "analysis": "患者刺痛固定、面色晦暗，为血液运行不畅，瘀血内停。",
                    "formula": "血府逐瘀汤", "formula_adjustment": "若胸痛加薤白；若腹痛加延胡索",
                    "treatment_principle": "活血化瘀", "confidence": 80,
                    "additional_notes": "演示模式：孕妇忌用，出血性疾病慎用。"}
        elif any(w in all_text for w in ["头晕", "目眩", "痰多", "恶心", "呕吐"]):
            return {"syndrome": "痰证", "syndrome_category": "气血津液辨证",
                    "analysis": "患者头晕目眩、痰多、恶心呕吐，为痰浊内停，阻滞气机。",
                    "formula": "半夏白术天麻汤", "formula_adjustment": "若眩晕甚加钩藤；若呕吐加竹茹",
                    "treatment_principle": "化痰息风、健脾祛湿", "confidence": 80,
                    "additional_notes": "演示模式：忌食肥甘厚味。"}
        else:
            return {"syndrome": "待辨证", "syndrome_category": "待分类",
                    "analysis": f"根据主诉「{chief_complaint}」和症状信息，建议补充更多四诊信息（望闻问切）以明确辨证。",
                    "formula": "待推荐", "formula_adjustment": "建议补充舌象脉象",
                    "treatment_principle": "四诊合参后确定", "confidence": 50,
                    "additional_notes": "💡 提示：配置 API Key 后可使用 AI 智能辨证功能。前往「系统设置」页面配置。"}

    def _load_knowledge_base(self) -> str:
        knowledge = """
【中医基础理论完整知识库】

一、六经辨证：太阳、阳明、少阳、太阴、少阴、厥阴
二、脏腑辨证：心、肝、脾、肺、肾
三、卫气营血辨证：卫分、气分、营分、血分
四、三焦辨证：上焦、中焦、下焦
五、八纲辨证：表里、寒热、虚实、阴阳
六、气血津液辨证：气虚、血虚、气滞、血瘀、痰证、饮证
七、常用方剂：麻黄汤、桂枝汤、小柴胡汤、白虎汤、逍遥散、四君子汤、六味地黄丸等
八、辨证论治流程：四诊合参→八纲辨证→脏腑辨证→确定证型→确定治法→选方用药
"""
        return knowledge

    def analyze_symptoms(self, chief_complaint: str, symptoms: List[str],
                        tongue_sign: str, pulse_sign: str) -> Dict:
        if not self.has_api_key:
            return self._rule_based_diagnosis(chief_complaint, symptoms, tongue_sign, pulse_sign)

        prompt = f"""
你是一位经验丰富的中医师，请根据以下问诊信息进行辨证论治。

【主诉】{chief_complaint}
【伴随症状】{', '.join(symptoms) if symptoms else '无'}
【舌象】{tongue_sign if tongue_sign else '未提供'}
【脉象】{pulse_sign if pulse_sign else '未提供'}

请基于中医辨证理论，完成以下分析：

1. 证型诊断（最准确的证型名称）
2. 辨证分析（200字以内）
3. 推荐方剂（最对症的经方或时方）
4. 方剂加减（50字以内）
5. 治疗原则
6. 信心指数（0-100）
7. 注意事项

请严格按照以下JSON格式返回：
{{
    "syndrome": "证型名称",
    "syndrome_category": "辨证体系",
    "analysis": "辨证分析",
    "formula": "方剂名称",
    "formula_adjustment": "方剂加减建议",
    "treatment_principle": "治疗原则",
    "confidence": 信心指数数字,
    "additional_notes": "注意事项"
}}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是一位中医辨证论治专家，精通《伤寒论》《金匮要略》《温病条辨》等经典。{self.knowledge_base}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "invalid_api_key" in error_msg.lower():
                return {"syndrome": "API Key 无效", "syndrome_category": "配置错误",
                        "analysis": "你输入的 API Key 无效或已过期。",
                        "formula": "无", "formula_adjustment": "无",
                        "treatment_principle": "无", "confidence": 0,
                        "additional_notes": "🔑 请检查 API Key 是否正确，或前往厂商官网重新获取。"}
            elif "404" in error_msg or "model" in error_msg.lower():
                return {"syndrome": "模型不存在", "syndrome_category": "配置错误",
                        "analysis": f"选择的模型 '{self.model}' 不存在或不可用。",
                        "formula": "无", "formula_adjustment": "无",
                        "treatment_principle": "无", "confidence": 0,
                        "additional_notes": "🤖 请在设置中选择其他模型，或检查厂商是否支持该模型。"}
            elif "429" in error_msg or "rate" in error_msg.lower():
                return {"syndrome": "请求频率超限", "syndrome_category": "限流",
                        "analysis": "API 请求过于频繁，请稍后重试。",
                        "formula": "无", "formula_adjustment": "无",
                        "treatment_principle": "无", "confidence": 0,
                        "additional_notes": "⏳ 请等待 30 秒后重试，或升级 API 套餐。"}
            elif "connection" in error_msg.lower() or "timeout" in error_msg.lower() or "connect" in error_msg.lower():
                return {"syndrome": "网络连接失败", "syndrome_category": "网络错误",
                        "analysis": f"无法连接到 {self.provider} 的 API 服务器。",
                        "formula": "无", "formula_adjustment": "无",
                        "treatment_principle": "无", "confidence": 0,
                        "additional_notes": f"🌐 请检查：\n1. 网络是否正常\n2. API 地址是否正确\n3. 当前网络是否能访问 {self.provider} 服务"}
            else:
                return {"syndrome": "诊断失败", "syndrome_category": "未知错误",
                        "analysis": f"AI 分析时发生错误：{error_msg[:300]}",
                        "formula": "无", "formula_adjustment": "无",
                        "treatment_principle": "无", "confidence": 0,
                        "additional_notes": "请截图此错误信息并联系开发者，或尝试切换其他 API 厂商。"}
