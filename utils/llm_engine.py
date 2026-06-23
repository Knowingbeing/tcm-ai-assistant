import os
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TCMDiagnosisEngine:
    def __init__(self, api_key: str = ""):
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY", "")
        self.has_api_key = bool(api_key) and api_key.startswith("sk-")
        if self.has_api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception:
                self.has_api_key = False
        self.knowledge_base = self._load_knowledge_base()

    def _rule_based_diagnosis(self, chief_complaint: str, symptoms: List[str],
                              tongue_sign: str, pulse_sign: str) -> Dict:
        all_text = chief_complaint + " " + " ".join(symptoms) + " " + tongue_sign + " " + pulse_sign

        # 感冒类
        if any(w in all_text for w in ["恶寒", "无汗", "鼻塞", "流清涕", "头身疼痛", "头痛", "身痛"]):
            return {"syndrome": "太阳伤寒证", "syndrome_category": "六经辨证",
                    "analysis": "患者恶寒、无汗、鼻塞流清涕、头身疼痛，为风寒之邪侵袭太阳经，卫阳被遏，营阴郁滞。",
                    "formula": "麻黄汤", "formula_adjustment": "若鼻塞重可加辛夷、苍耳子；若咳嗽加杏仁",
                    "treatment_principle": "发汗解表、宣肺平喘", "confidence": 80,
                    "additional_notes": "演示模式：服药后温覆取微汗，忌食生冷。配置 API Key 可获得更精准的 AI 辨证。"}
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

        # 少阳/阳明
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

        # 肝系
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

        # 心系
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

        # 脾系
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

        # 肺系
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

        # 肾系
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

        # 气血津液
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

        # 默认
        else:
            return {"syndrome": "待辨证", "syndrome_category": "待分类",
                    "analysis": f"根据主诉「{chief_complaint}」和症状信息，建议补充更多四诊信息（望闻问切）以明确辨证。当前为演示模式，可尝试输入以下关键词触发自动诊断：恶寒、发热、头痛、咳嗽、失眠、乏力、腰痛、腹泻等。",
                    "formula": "待推荐", "formula_adjustment": "建议补充舌象脉象",
                    "treatment_principle": "四诊合参后确定", "confidence": 50,
                    "additional_notes": "💡 提示：演示模式支持 20+ 种常见证型的自动识别。配置 OpenAI API Key 后可使用 AI 智能辨证功能，前往「系统设置」页面配置。"}

    def _load_knowledge_base(self) -> str:
        knowledge = """
【中医基础理论完整知识库】

═══════════════════════════════════════════════════════════════════
一、阴阳五行学说
═══════════════════════════════════════════════════════════════════

【阴阳学说】
- 阴阳对立制约：阴阳双方存在相互对立、相互制约的关系
- 阴阳互根互用：阴阳双方存在相互依存、相互为用的关系
- 阴阳消长平衡：阴阳双方处于不断的消长变化之中
- 阴阳相互转化：阴阳在一定条件下可以相互转化

【五行学说】
- 木：肝、胆、目、筋、怒、酸、春、东、风、生
- 火：心、小肠、舌、脉、喜、苦、夏、南、暑、长
- 土：脾、胃、口、肉、思、甘、长夏、中、湿、化
- 金：肺、大肠、鼻、皮、悲、辛、秋、西、燥、收
- 水：肾、膀胱、耳、骨、恐、咸、冬、北、寒、藏

五行相生：木→火→土→金→水→木
五行相克：木→土→水→火→金→木

═══════════════════════════════════════════════════════════════════
二、藏象学说
═══════════════════════════════════════════════════════════════════

【心】主血脉、主神明、开窍于舌、其华在面
- 心气虚：心悸气短、活动后加重、自汗
- 心血虚：心悸失眠、多梦、头晕健忘
- 心火亢盛：心烦失眠、口舌生疮、小便短赤
- 心血瘀阻：心胸憋闷疼痛、痛引肩背

【肺】主气司呼吸、主宣发肃降、通调水道、朝百脉、主皮毛、开窍于鼻
- 肺气虚：咳喘无力、气短自汗
- 肺阴虚：干咳少痰、潮热盗汗
- 风寒犯肺：咳嗽痰稀、鼻塞流清涕
- 风热犯肺：咳嗽痰黄、口渴咽痛
- 痰热壅肺：咳嗽气喘、痰多黄稠

【脾】主运化、主升清、主统血、主肌肉四肢、开窍于口、其华在唇
- 脾气虚：纳少腹胀、便溏、乏力
- 脾阳虚：腹胀纳少、腹痛喜温喜按
- 脾不统血：便血、尿血、月经过多
- 寒湿困脾：脘腹痞闷、便溏、头身困重
- 湿热蕴脾：脘腹痞闷、便溏不爽、面目发黄

【肝】主疏泄、主藏血、主筋、开窍于目、其华在爪
- 肝气郁结：胸胁胀痛、善太息、情志抑郁
- 肝火上炎：头胀头痛、面红目赤、急躁易怒
- 肝血虚：眩晕耳鸣、夜盲、肢体麻木
- 肝阳上亢：眩晕耳鸣、头目胀痛、腰膝酸软

【肾】藏精主生长发育生殖、主水、主纳气、主骨生髓、开窍于耳及二阴、其华在发
- 肾阳虚：畏寒肢冷、腰膝酸软、阳痿早泄
- 肾阴虚：腰膝酸软、头晕耳鸣、潮热盗汗
- 肾精不足：发育迟缓、早衰、健忘恍惚
- 肾不纳气：呼多吸少、动则气喘

═══════════════════════════════════════════════════════════════════
三、气血津液辨证
═══════════════════════════════════════════════════════════════════

【气病辨证】
- 气虚证：神疲乏力、气短懒言、自汗
- 气陷证：气虚证+久泻脱肛、内脏下垂
- 气滞证：胀闷疼痛、走窜不定、随情志变化
- 气逆证：咳喘、呕恶、头痛眩晕

【血病辨证】
- 血虚证：面色淡白、唇甲色淡、头晕心悸
- 血瘀证：刺痛固定、面色晦暗、舌紫暗有瘀斑
- 血热证：出血色鲜红、身热、口渴
- 血寒证：手足冷痛、肤色紫暗、月经色暗有块

【津液辨证】
- 痰证：胸闷、痰多、body重、头晕目眩
- 饮证：胸胁胀满、咳唾引痛、水肿
- 津亏证：口燥咽干、皮肤干枯、大便干结

═══════════════════════════════════════════════════════════════════
四、六经辨证（《伤寒论》核心）
═══════════════════════════════════════════════════════════════════

【太阳病】
- 太阳伤寒证（表实证）：恶寒发热、头痛项强、无汗、脉浮紧
  → 麻黄汤
- 太阳中风证（表虚证）：发热汗出、恶风、脉浮缓
  → 桂枝汤
- 太阳蓄水证：发热恶寒、小便不利、消渴
  → 五苓散
- 太阳蓄血证：少腹急结、小便自利、发狂
  → 桃核承气汤

【阳明病】
- 阳明经证（热证）：身大热、汗大出、口大渴、脉洪大
  → 白虎汤
- 阳明腑实证（实证）：潮热谵语、腹满硬痛、大便秘结
  → 大承气汤

【少阳病】
- 少阳病证：往来寒热、胸胁苦满、口苦咽干目眩、脉弦
  → 小柴胡汤

【太阴病】
- 太阴病证：腹满呕吐、食不下、自利、腹痛喜温喜按
  → 理中丸

【少阴病】
- 少阴寒化证：畏寒蜷卧、四肢厥冷、下利清谷、脉微细
  → 四逆汤
- 少阴热化证：心烦不得眠、口燥咽干、舌尖红
  → 黄连阿胶汤

【厥阴病】
- 厥阴病证：消渴、气上撞心、心中疼热、饥不欲食
  → 乌梅丸

═══════════════════════════════════════════════════════════════════
五、卫气营血辨证（温病学核心）
═══════════════════════════════════════════════════════════════════

【卫分证】
- 温邪初袭，卫表失宣
- 发热、微恶风寒、头痛、口微渴、舌边尖红、脉浮数
- 治法：辛凉解表 → 银翘散、桑菊饮

【气分证】
- 邪热亢盛，正邪剧争
- 壮热、不恶寒反恶热、汗多、渴喜冷饮、舌红苔黄、脉洪数
- 治法：清气泄热 → 白虎汤、麻杏石甘汤

【营分证】
- 热灼营阴，扰神窜络
- 身热夜甚、心烦不寐、斑疹隐隐、口不甚渴、舌红绛、脉细数
- 治法：清营透热 → 清营汤

【血分证】
- 热盛动血，耗阴动风
- 身热、出血、斑疹显露、神昏谵语、抽搐、舌深绛、脉细数
- 治法：凉血散血 → 犀角地黄汤

═══════════════════════════════════════════════════════════════════
六、三焦辨证（温病学）
═══════════════════════════════════════════════════════════════════

【上焦病证】
- 手太阴肺：发热恶寒、咳嗽、口微渴
- 手厥阴心包：神昏谵语、舌謇肢厥

【中焦病证】
- 足阳明胃：身热、汗出、口渴、脉数
- 足太阴脾：身热不扬、脘腹胀满、便溏

【下焦病证】
- 足少阴肾：身热颧红、手足心热、口燥咽干
- 足厥阴肝：手足蠕动、瘛疭、神倦

═══════════════════════════════════════════════════════════════════
七、八纲辨证
═══════════════════════════════════════════════════════════════════

【表里辨证】
- 表证：恶寒发热同时出现、头身疼痛、舌苔薄白、脉浮
- 里证：但寒不热或但热不寒、脏腑症状为主

【寒热辨证】
- 寒证：恶寒喜暖、口不渴、面色苍白、肢冷蜷卧、小便清长、大便稀溏
- 热证：发热恶热、口渴喜冷饮、面红目赤、烦躁不宁、小便短赤、大便干结

【虚实辨证】
- 虚证：神疲乏力、声低懒言、隐痛喜按、脉虚无力
- 实证：精神亢奋、声高气粗、疼痛拒按、脉实有力

【阴阳辨证】
- 阴证：里、寒、虚证的概括
- 阳证：表、热、实证的概括

═══════════════════════════════════════════════════════════════════
八、十问纲要
═══════════════════════════════════════════════════════════════════

1. 寒热：有无发热恶寒？寒热特点？
2. 汗：有无出汗？自汗还是盗汗？时间？
3. 头身：头痛部位？身痛？眩晕？
4. 便：大便颜色、质地、次数？小便颜色、量？
5. 饮食：食欲？口味？口渴？饮水？
6. 胸腹：胸闷？腹胀？腹痛？
7. 耳目：听力？视力？耳鸣？
8. 睡眠：失眠？多梦？嗜睡？
9. 旧病：既往病史？过敏史？
10. 妇女：月经周期？经量？经色？带下？

═══════════════════════════════════════════════════════════════════
九、舌诊要点
═══════════════════════════════════════════════════════════════════

【舌色】
- 淡红舌：正常
- 淡白舌：气血虚、阳虚
- 红舌：热证（实热或虚热）
- 绛舌：热盛（营血分热）
- 紫舌：瘀血

【舌形】
- 胖大舌：水肿、痰湿
- 瘦薄舌：阴虚、气血虚
- 齿痕舌：脾虚、水湿
- 裂纹舌：阴虚、血虚

【舌苔】
- 白苔：寒证、表证
- 黄苔：热证
- 灰黑苔：热极或寒极
- 薄苔：正常或表证
- 厚苔：里证、食积
- 腻苔：痰湿、食积
- 剥苔：阴虚、胃气虚

═══════════════════════════════════════════════════════════════════
十、脉诊要点
═══════════════════════════════════════════════════════════════════

【浮脉类】浮、洪、濡、散、芤、革
- 浮脉：轻取即得，主表证
- 洪脉：脉来如波涛汹涌，主热盛

【沉脉类】沉、伏、牢、弱、细
- 沉脉：重按始得，主里证
- 细脉：脉细如线，主气血虚

【迟脉类】迟、缓、涩、结
- 迟脉：一息不足四至（<60次/分），主寒证
- 结脉：脉来缓慢，时有中止，主阴盛气结

【数脉类】数、疾、促、动
- 数脉：一息五至以上（>90次/分），主热证
- 促脉：脉来急促，时有中止，主阳热亢盛

【虚脉类】虚、微、散、短
- 虚脉：举按皆无力，主虚证
- 微脉：极细极软，主阳气衰微

【实脉类】实、滑、弦、紧、长
- 实脉：举按皆有力，主实证
- 滑脉：往来流利，主痰饮、食积、孕妇
- 弦脉：端直以长，主肝胆病、痛证、痰饮

═══════════════════════════════════════════════════════════════════
十一、常用方剂分类
═══════════════════════════════════════════════════════════════════

【解表剂】
辛温解表：麻黄汤、桂枝汤、小青龙汤、大青龙汤
辛凉解表：银翘散、桑菊饮、麻杏石甘汤

【泻下剂】
寒下：大承气汤、小承气汤、调胃承气汤
温下：大黄附子汤
润下：麻子仁丸

【和解剂】
和解少阳：小柴胡汤、大柴胡汤
调和肝脾：逍遥散、痛泻要方
调和寒热：半夏泻心汤

【清热剂】
清气分热：白虎汤、竹叶石膏汤
清营凉血：清营汤、犀角地黄汤
清热解毒：黄连解毒汤、五味消毒饮
清脏腑热：龙胆泻肝汤、导赤散、清胃散、白头翁汤

【温里剂】
温中散寒：理中丸、小建中汤
回阳救逆：四逆汤、参附汤
温经散寒：当归四逆汤

【补益剂】
补气：四君子汤、补中益气汤
补血：四物汤、当归补血汤
气血双补：八珍汤、归脾汤
补阴：六味地黄丸、大补阴丸
补阳：金匮肾气丸、右归丸
阴阳双补：地黄饮子

【理气剂】
行气：柴胡疏肝散、越鞠丸、半夏厚朴汤
降气：旋覆代赭汤、橘皮竹茹汤

【理血剂】
活血化瘀：血府逐瘀汤、补阳还五汤、桃红四物汤
止血：十灰散、小蓟饮子

【祛湿剂】
化湿和胃：平胃散、藿香正气散
清热祛湿：茵陈蒿汤、八正散
利水渗湿：五苓散、五皮散
温化水湿：真武汤、实脾饮
祛风胜湿：独活寄生汤

【祛痰剂】
燥湿化痰：二陈汤、温胆汤
清热化痰：清气化痰丸
润燥化痰：贝母瓜蒌散
温化寒痰：苓甘五味姜辛汤
治风化痰：半夏白术天麻汤

【安神剂】
重镇安神：朱砂安神丸
滋养安神：酸枣仁汤、天王补心丹

【固涩剂】
固表止汗：牡蛎散
涩肠固脱：四神丸
涩精止遗：金锁固精丸

═══════════════════════════════════════════════════════════════════
十二、辨证论治流程
═══════════════════════════════════════════════════════════════════

1. 四诊合参：望、闻、问、切收集病情资料
2. 八纲辨证：确定表里、寒热、虚实、阴阳
3. 脏腑辨证：定位到具体脏腑
4. 病因辨证：确定病因（六淫、七情、痰瘀等）
5. 确定证型：综合判断，确定证型
6. 确定治法：根据证型确定治疗原则
7. 选方用药：根据治法选择方剂，随证加减
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

1. 证型诊断（请给出最准确的证型名称，可以是六经辨证、脏腑辨证、卫气营血辨证或气血津液辨证的证型）

2. 辨证分析（200字以内）：
   - 分析病因病机
   - 说明为何诊断为此证型
   - 鉴别诊断（与类似证型的区别）

3. 推荐方剂（请给出最对症的经方或时方）

4. 方剂加减（50字以内）：根据具体症状建议的药物加减

5. 治疗原则：确定的治法

6. 信心指数（0-100）：你对此诊断的信心程度

7. 注意事项：服药禁忌或生活调护建议

请严格按照以下JSON格式返回：
{{
    "syndrome": "证型名称",
    "syndrome_category": "辨证体系（六经/脏腑/卫气营血/气血津液）",
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
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"你是一位中医辨证论治专家，精通《伤寒论》《金匮要略》《温病条辨》等经典。以下是你掌握的中医知识：{self.knowledge_base}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        except Exception as e:
            return {
                "syndrome": "待诊断",
                "syndrome_category": "待分类",
                "analysis": f"分析失败：{str(e)}",
                "formula": "待推荐",
                "formula_adjustment": "无",
                "treatment_principle": "待确定",
                "confidence": 0,
                "additional_notes": "请手动诊断"
            }

    def get_syndrome_explanation(self, syndrome_name: str) -> str:
        prompt = f"""
请详细解释中医证型"{syndrome_name}"：
1. 定义与病因病机
2. 主要症状与舌脉表现
3. 治疗原则与代表方剂
4. 鉴别诊断（与类似证型的区别）
用200字以内回答。
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一位中医基础理论专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"获取解释失败：{str(e)}"

    def get_formula_details(self, formula_name: str) -> str:
        prompt = f"""
请详细解释方剂"{formula_name}"：
1. 组成与方义分析
2. 功效与主治
3. 临床应用要点
4. 加减变化
用200字以内回答。
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一位方剂学专家。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"获取解释失败：{str(e)}"
