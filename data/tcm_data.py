FORMULAS = [
    # 解表剂
    {"name": "麻黄汤", "composition": "麻黄、桂枝、杏仁、炙甘草", "function": "发汗解表、宣肺平喘", "indication": "外感风寒表实证：恶寒发热、头身疼痛、无汗而喘", "source": "《伤寒论》", "category": "解表剂"},
    {"name": "桂枝汤", "composition": "桂枝、芍药、生姜、大枣、炙甘草", "function": "解肌发表、调和营卫", "indication": "外感风寒表虚证：发热汗出、恶风头痛", "source": "《伤寒论》", "category": "解表剂"},
    {"name": "小青龙汤", "composition": "麻黄、桂枝、芍药、半夏、细辛、干姜、五味子", "function": "解表散寒、温肺化饮", "indication": "外寒内饮证：恶寒发热、咳喘痰多清稀", "source": "《伤寒论》", "category": "解表剂"},
    {"name": "大青龙汤", "composition": "麻黄、桂枝、杏仁、石膏、生姜、大枣", "function": "发汗解表、清热除烦", "indication": "外寒里热证：恶寒发热、烦躁口渴", "source": "《伤寒论》", "category": "解表剂"},
    {"name": "银翘散", "composition": "银花、连翘、桔梗、薄荷、竹叶、生甘草、荆芥穗", "function": "辛凉解表、清热解毒", "indication": "温病初起：发热微恶风寒、咽痛口渴", "source": "《温病条辨》", "category": "解表剂"},
    {"name": "桑菊饮", "composition": "桑叶、菊花、杏仁、连翘、薄荷、桔梗、甘草", "function": "疏风清热、宣肺止咳", "indication": "风温初起：咳嗽、身热不甚", "source": "《温病条辨》", "category": "解表剂"},
    {"name": "麻杏石甘汤", "composition": "麻黄、杏仁、石膏、炙甘草", "function": "辛凉宣泄、清热平喘", "indication": "外感风热咳喘：发热咳喘、口渴", "source": "《伤寒论》", "category": "解表剂"},
    {"name": "九味羌活汤", "composition": "羌活、防风、苍术、细辛、川芎、白芷、生地、黄芩、甘草", "function": "发汗祛湿、兼清里热", "indication": "外感风寒湿邪：恶寒发热、头身酸痛", "source": "《此事难知》", "category": "解表剂"},
    {"name": "香苏散", "composition": "香附、紫苏叶、陈皮、炙甘草", "function": "疏风散寒、理气和中", "indication": "外感风寒兼气滞：恶寒发热、头痛无汗", "source": "《太平惠民和剂局方》", "category": "解表剂"},

    # 清热剂
    {"name": "白虎汤", "composition": "石膏、知母、炙甘草、粳米", "function": "清热生津", "indication": "阳明经证：身大热、汗大出、口大渴", "source": "《伤寒论》", "category": "清热剂"},
    {"name": "黄连解毒汤", "composition": "黄连、黄芩、黄柏、栀子", "function": "泻火解毒", "indication": "三焦火毒热盛证：大热烦躁、口燥咽干", "source": "《外台秘要》", "category": "清热剂"},
    {"name": "龙胆泻肝汤", "composition": "龙胆草、黄芩、栀子、泽泻、木通、车前子、当归、柴胡、生地黄", "function": "泻肝胆实火、清下焦湿热", "indication": "肝胆实火上炎或湿热下注", "source": "《医方集解》", "category": "清热剂"},
    {"name": "导赤散", "composition": "生地黄、木通、竹叶、甘草", "function": "清心养阴、利水通淋", "indication": "心经火热证：心胸烦热、口舌生疮", "source": "《小儿药证直诀》", "category": "清热剂"},
    {"name": "白头翁汤", "composition": "白头翁、黄连、黄柏、秦皮", "function": "清热解毒、凉血止痢", "indication": "热毒血痢：腹痛里急后重", "source": "《伤寒论》", "category": "清热剂"},
    {"name": "清胃散", "composition": "黄连、升麻、当归、生地黄、牡丹皮", "function": "清胃凉血", "indication": "胃火牙痛：牙痛牵引头痛、口气热臭", "source": "《脾胃论》", "category": "清热剂"},
    {"name": "芍药汤", "composition": "芍药、当归、黄连、槟榔、木香、大黄、黄芩、肉桂、甘草", "function": "清热燥湿、调气和血", "indication": "湿热痢疾：腹痛便脓血、里急后重", "source": "《素问病机气宜保命集》", "category": "清热剂"},

    # 泻下剂
    {"name": "大承气汤", "composition": "大黄、芒硝、枳实、厚朴", "function": "峻下热结", "indication": "阳明腑实证：大便不通、腹满硬痛", "source": "《伤寒论》", "category": "泻下剂"},
    {"name": "小承气汤", "composition": "大黄、枳实、厚朴", "function": "轻下热结", "indication": "阳明腑实轻证：谵语潮热、大便硬", "source": "《伤寒论》", "category": "泻下剂"},
    {"name": "调胃承气汤", "composition": "大黄、芒硝、炙甘草", "function": "缓下热结", "indication": "阳明燥热内结：蒸蒸发热、心烦腹满", "source": "《伤寒论》", "category": "泻下剂"},
    {"name": "麻子仁丸", "composition": "麻子仁、芍药、枳实、大黄、厚朴、杏仁", "function": "润肠泄热、行气通便", "indication": "胃肠燥热便秘：大便干结、小便频数", "source": "《伤寒论》", "category": "泻下剂"},

    # 和解剂
    {"name": "小柴胡汤", "composition": "柴胡、黄芩、人参、半夏、炙甘草、生姜、大枣", "function": "和解少阳", "indication": "少阳病：往来寒热、胸胁苦满、口苦咽干", "source": "《伤寒论》", "category": "和解剂"},
    {"name": "大柴胡汤", "composition": "柴胡、黄芩、芍药、半夏、枳实、大黄、生姜、大枣", "function": "和解少阳、内泻热结", "indication": "少阳阳明合病：往来寒热、心下急痛", "source": "《伤寒论》", "category": "和解剂"},
    {"name": "逍遥散", "composition": "柴胡、当归、白芍、白术、茯苓、生姜、薄荷", "function": "疏肝解郁、养血健脾", "indication": "肝郁血虚脾弱证：两胁作痛、神疲食少", "source": "《太平惠民和剂局方》", "category": "和解剂"},
    {"name": "丹栀逍遥散", "composition": "柴胡、当归、白芍、白术、茯苓、薄荷、牡丹皮、栀子", "function": "疏肝清热、养血健脾", "indication": "肝郁化火证：烦躁易怒、潮热", "source": "《内科摘要》", "category": "和解剂"},
    {"name": "半夏泻心汤", "composition": "半夏、黄芩、黄连、人参、干姜、炙甘草、大枣", "function": "和胃降逆、开结除痞", "indication": "寒热互结心下痞：心下痞满、呕吐", "source": "《伤寒论》", "category": "和解剂"},
    {"name": "痛泻要方", "composition": "白术、白芍、陈皮、防风", "function": "补脾柔肝、祛湿止泻", "indication": "痛泻：肠鸣腹痛、大便泄泻", "source": "《医学心悟》", "category": "和解剂"},

    # 补益剂
    {"name": "四君子汤", "composition": "人参、白术、茯苓、炙甘草", "function": "益气健脾", "indication": "脾胃气虚证：面色萎白、食少便溏", "source": "《太平惠民和剂局方》", "category": "补益剂"},
    {"name": "补中益气汤", "composition": "黄芪、人参、白术、甘草、当归、陈皮、升麻、柴胡", "function": "补中益气、升阳举陷", "indication": "脾虚气陷证：体倦乏力、久泻脱肛", "source": "《脾胃论》", "category": "补益剂"},
    {"name": "归脾汤", "composition": "黄芪、人参、白术、茯神、当归、远志、酸枣仁、龙眼肉", "function": "益气补血、健脾养心", "indication": "心脾两虚证：心悸失眠、体倦食少", "source": "《济生方》", "category": "补益剂"},
    {"name": "六味地黄丸", "composition": "熟地黄、山药、山茱萸、牡丹皮、泽泻、茯苓", "function": "滋阴补肾", "indication": "肾阴虚证：腰膝酸软、头晕耳鸣", "source": "《小儿药证直诀》", "category": "补益剂"},
    {"name": "金匮肾气丸", "composition": "熟地黄、山药、山茱萸、牡丹皮、泽泻、茯苓、桂枝、附子", "function": "温补肾阳", "indication": "肾阳虚证：腰膝酸软、畏寒肢冷", "source": "《金匮要略》", "category": "补益剂"},
    {"name": "四物汤", "composition": "当归、川芎、白芍、熟地黄", "function": "补血调血", "indication": "营血虚滞证：头晕心悸、月经不调", "source": "《仙授理伤续断秘方》", "category": "补益剂"},
    {"name": "八珍汤", "composition": "人参、白术、茯苓、甘草、当归、川芎、白芍、熟地黄", "function": "气血双补", "indication": "气血两虚证：面色苍白、头晕目眩", "source": "《正体类要》", "category": "补益剂"},
    {"name": "炙甘草汤", "composition": "炙甘草、人参、桂枝、生姜、阿胶、生地黄、麦冬、麻仁、大枣", "function": "益气滋阴、通阳复脉", "indication": "气阴两虚证：脉结代、心动悸", "source": "《伤寒论》", "category": "补益剂"},
    {"name": "一贯煎", "composition": "北沙参、麦冬、当归、生地黄、枸杞子、川楝子", "function": "滋阴疏肝", "indication": "肝肾阴虚、肝气不舒：胸脘胁痛", "source": "《续名医类案》", "category": "补益剂"},
    {"name": "左归丸", "composition": "熟地黄、山药、山茱萸、枸杞子、菟丝子、鹿角胶、龟板胶、川牛膝", "function": "滋阴补肾、填精益髓", "indication": "真阴不足证：头晕目眩、腰酸腿软", "source": "《景岳全书》", "category": "补益剂"},
    {"name": "右归丸", "composition": "熟地黄、山药、山茱萸、枸杞子、菟丝子、鹿角胶、杜仲、肉桂、附子、当归", "function": "温补肾阳、填精益髓", "indication": "肾阳不足证：畏寒肢冷、阳痿遗精", "source": "《景岳全书》", "category": "补益剂"},

    # 理气剂
    {"name": "柴胡疏肝散", "composition": "柴胡、陈皮、川芎、香附、枳壳、芍药、炙甘草", "function": "疏肝理气、活血止痛", "indication": "肝气郁结证：胁肋疼痛、胸闷善太息", "source": "《景岳全书》", "category": "理气剂"},
    {"name": "越鞠丸", "composition": "香附、川芎、苍术、栀子、神曲", "function": "行气解郁", "indication": "六郁证：胸膈痞闷、脘腹胀痛", "source": "《丹溪心法》", "category": "理气剂"},
    {"name": "半夏厚朴汤", "composition": "半夏、厚朴、茯苓、生姜、紫苏叶", "function": "行气散结、降逆化痰", "indication": "梅核气：咽中如有物阻", "source": "《金匮要略》", "category": "理气剂"},
    {"name": "枳实薤白桂枝汤", "composition": "枳实、薤白、桂枝、厚朴、瓜蒌", "function": "通阳散结、祛痰下气", "indication": "胸痹：胸满而痛、喘息咳唾", "source": "《金匮要略》", "category": "理气剂"},

    # 理血剂
    {"name": "血府逐瘀汤", "composition": "桃仁、红花、当归、川芎、赤芍、牛膝、桔梗、柴胡、枳壳", "function": "活血化瘀、行气止痛", "indication": "胸中血瘀证：胸痛头痛、痛如针刺", "source": "《医林改错》", "category": "理血剂"},
    {"name": "补阳还五汤", "composition": "黄芪、当归尾、赤芍、地龙、川芎、红花、桃仁", "function": "补气活血通络", "indication": "气虚血瘀证：半身不遂、口眼歪斜", "source": "《医林改错》", "category": "理血剂"},
    {"name": "桃核承气汤", "composition": "桃仁、大黄、桂枝、芒硝、炙甘草", "function": "破血逐瘀", "indication": "太阳蓄血证：少腹急结、其人如狂", "source": "《伤寒论》", "category": "理血剂"},
    {"name": "生化汤", "composition": "当归、川芎、桃仁、炮姜、炙甘草", "function": "化瘀生新、温经止痛", "indication": "产后瘀血腹痛：恶露不行", "source": "《傅青主女科》", "category": "理血剂"},

    # 祛湿剂
    {"name": "平胃散", "composition": "苍术、厚朴、陈皮、炙甘草", "function": "燥湿运脾、行气和胃", "indication": "湿滞脾胃证：脘腹胀满、不思饮食", "source": "《简要济众方》", "category": "祛湿剂"},
    {"name": "藿香正气散", "composition": "藿香、紫苏、白芷、大腹皮、茯苓、白术、半夏曲、陈皮", "function": "解表化湿、理气和中", "indication": "外感风寒内伤湿滞：上吐下泻", "source": "《太平惠民和剂局方》", "category": "祛湿剂"},
    {"name": "茵陈蒿汤", "composition": "茵陈、栀子、大黄", "function": "清热利湿退黄", "indication": "湿热黄疸：面目俱黄、小便短赤", "source": "《伤寒论》", "category": "祛湿剂"},
    {"name": "五苓散", "composition": "猪苓、泽泻、白术、茯苓、桂枝", "function": "利水渗湿、温阳化气", "indication": "蓄水证：小便不利、头痛微热", "source": "《伤寒论》", "category": "祛湿剂"},
    {"name": "真武汤", "composition": "附子、茯苓、芍药、白术、生姜", "function": "温阳利水", "indication": "阳虚水泛证：心悸头眩、四肢沉重", "source": "《伤寒论》", "category": "祛湿剂"},
    {"name": "独活寄生汤", "composition": "独活、桑寄生、杜仲、牛膝、细辛、秦艽、茯苓、肉桂、防风、川芎、人参、甘草、当归、芍药、干地黄", "function": "祛风湿、止痹痛、益肝肾、补气血", "indication": "痹证日久：腰膝冷痛、肢节屈伸不利", "source": "《备急千金要方》", "category": "祛湿剂"},

    # 祛痰剂
    {"name": "二陈汤", "composition": "半夏、橘红、茯苓、炙甘草、生姜、乌梅", "function": "燥湿化痰、理气和中", "indication": "痰湿证：咳嗽痰多、恶心呕吐", "source": "《太平惠民和剂局方》", "category": "祛痰剂"},
    {"name": "温胆汤", "composition": "半夏、竹茹、枳实、陈皮、茯苓、炙甘草", "function": "理气化痰、和胃利胆", "indication": "胆郁痰扰证：胆怯易惊、呕恶呃逆", "source": "《三因极一病证方论》", "category": "祛痰剂"},
    {"name": "半夏白术天麻汤", "composition": "半夏、白术、天麻、茯苓、橘红、炙甘草", "function": "化痰息风、健脾祛湿", "indication": "风痰上扰证：眩晕头痛、胸闷呕恶", "source": "《医学心悟》", "category": "祛痰剂"},
    {"name": "清气化痰丸", "composition": "陈皮、杏仁、枳实、黄芩、瓜蒌仁、茯苓、胆南星、制半夏", "function": "清热化痰、理气止咳", "indication": "痰热咳嗽：痰稠色黄、咯之不爽", "source": "《医方考》", "category": "祛痰剂"},
    {"name": "小陷胸汤", "composition": "黄连、半夏、瓜蒌实", "function": "清热化痰、宽胸散结", "indication": "痰热互结证：胸脘痞闷、按之则痛", "source": "《伤寒论》", "category": "祛痰剂"},

    # 安神剂
    {"name": "酸枣仁汤", "composition": "酸枣仁、茯苓、知母、川芎、甘草", "function": "养血安神、清热除烦", "indication": "虚烦不眠：心悸失眠、头目眩晕", "source": "《金匮要略》", "category": "安神剂"},
    {"name": "天王补心丹", "composition": "生地黄、人参、丹参、玄参、茯苓、远志、酸枣仁、柏子仁", "function": "滋阴养血、补心安神", "indication": "阴虚血少神志不安：心悸失眠", "source": "《摄生秘剖》", "category": "安神剂"},
    {"name": "朱砂安神丸", "composition": "朱砂、黄连、炙甘草、生地黄、当归", "function": "镇心安神、清热养血", "indication": "心火亢盛、阴血不足证：失眠多梦", "source": "《内外伤辨惑论》", "category": "安神剂"},

    # 固涩剂
    {"name": "牡蛎散", "composition": "黄芪、麻黄根、牡蛎", "function": "益气固表、敛阴止汗", "indication": "自汗盗汗：自汗出、夜卧更甚", "source": "《太平惠民和剂局方》", "category": "固涩剂"},
    {"name": "金锁固精丸", "composition": "沙苑蒺藜、芡实、莲须、龙骨、牡蛎、莲子", "function": "补肾涩精", "indication": "肾虚遗精：遗精滑泄、腰酸耳鸣", "source": "《医方集解》", "category": "固涩剂"},
    {"name": "四神丸", "composition": "肉豆蔻、补骨脂、五味子、吴茱萸", "function": "温肾暖脾、涩肠止泻", "indication": "肾泻：五更泄泻、不思饮食", "source": "《证治准绳》", "category": "固涩剂"},

    # 治风剂
    {"name": "川芎茶调散", "composition": "川芎、荆芥、薄荷、羌活、白芷、细辛、防风、甘草", "function": "疏风止痛", "indication": "外感风邪头痛：偏正头痛", "source": "《太平惠民和剂局方》", "category": "治风剂"},
    {"name": "牵正散", "composition": "白附子、白僵蚕、全蝎", "function": "祛风化痰通络", "indication": "风中经络口眼歪斜", "source": "《杨氏家藏方》", "category": "治风剂"},
    {"name": "天麻钩藤饮", "composition": "天麻、钩藤、石决明、栀子、黄芩、牛膝、杜仲、益母草、桑寄生、夜交藤、茯神", "function": "平肝息风、清热活血、补益肝肾", "indication": "肝阳上亢、肝风上扰：头痛眩晕", "source": "《杂病证治新义》", "category": "治风剂"},

    # 治燥剂
    {"name": "杏苏散", "composition": "苏叶、杏仁、半夏、茯苓、前胡、桔梗、枳壳、甘草、生姜、大枣", "function": "轻宣凉燥、理肺化痰", "indication": "外感凉燥证：恶寒无汗、咳嗽痰稀", "source": "《温病条辨》", "category": "治燥剂"},
    {"name": "麦门冬汤", "composition": "麦冬、半夏、人参、甘草、粳米、大枣", "function": "清养肺胃、降逆下气", "indication": "虚热肺痿：咳唾涎沫", "source": "《金匮要略》", "category": "治燥剂"},
    {"name": "百合固金汤", "composition": "百合、生地黄、熟地黄、麦冬、白芍、当归、贝母、玄参、桔梗、甘草", "function": "滋养肺肾、化痰止咳", "indication": "肺肾阴虚：咳痰带血、咽喉燥痛", "source": "《慎斋遗书》", "category": "治燥剂"},
]

SYNDROMES = [
    # 六经辨证
    {"name": "太阳伤寒证", "category": "六经辨证", "symptoms": "恶寒发热、头痛项强、无汗而喘", "tongue": "舌苔薄白", "pulse": "脉浮紧", "formula": "麻黄汤", "treatment": "发汗解表、宣肺平喘"},
    {"name": "太阳中风证", "category": "六经辨证", "symptoms": "发热汗出、恶风头痛", "tongue": "舌苔薄白", "pulse": "脉浮缓", "formula": "桂枝汤", "treatment": "解肌发表、调和营卫"},
    {"name": "太阳蓄水证", "category": "六经辨证", "symptoms": "发热恶寒、小便不利、消渴", "tongue": "舌苔白", "pulse": "脉浮", "formula": "五苓散", "treatment": "化气行水"},
    {"name": "太阳蓄血证", "category": "六经辨证", "symptoms": "少腹急结、小便自利、发狂", "tongue": "舌紫暗", "pulse": "脉沉涩", "formula": "桃核承气汤", "treatment": "破血逐瘀"},
    {"name": "少阳病证", "category": "六经辨证", "symptoms": "往来寒热、胸胁苦满、口苦咽干", "tongue": "舌苔薄白", "pulse": "脉弦", "formula": "小柴胡汤", "treatment": "和解少阳"},
    {"name": "阳明经证", "category": "六经辨证", "symptoms": "身大热、汗大出、口大渴", "tongue": "舌苔黄燥", "pulse": "脉洪大", "formula": "白虎汤", "treatment": "清热生津"},
    {"name": "阳明腑实证", "category": "六经辨证", "symptoms": "潮热谵语、腹满硬痛、大便秘结", "tongue": "舌苔黄厚燥", "pulse": "脉沉实", "formula": "大承气汤", "treatment": "峻下热结"},
    {"name": "太阴病证", "category": "六经辨证", "symptoms": "腹满呕吐、食不下、自利腹痛", "tongue": "舌淡苔白", "pulse": "脉沉缓", "formula": "理中丸", "treatment": "温中散寒、健脾燥湿"},
    {"name": "少阴寒化证", "category": "六经辨证", "symptoms": "畏寒蜷卧、四肢厥冷、下利清谷", "tongue": "舌淡苔白", "pulse": "脉微细", "formula": "四逆汤", "treatment": "回阳救逆"},
    {"name": "少阴热化证", "category": "六经辨证", "symptoms": "心烦不得眠、口燥咽干", "tongue": "舌红少苔", "pulse": "脉细数", "formula": "黄连阿胶汤", "treatment": "滋阴降火"},
    {"name": "厥阴病证", "category": "六经辨证", "symptoms": "消渴、气上撞心、心中疼热", "tongue": "舌苔白或黄", "pulse": "脉弦", "formula": "乌梅丸", "treatment": "寒热并用"},

    # 脏腑辨证 - 心系
    {"name": "心气虚证", "category": "脏腑辨证", "symptoms": "心悸气短、活动后加重、自汗", "tongue": "舌淡苔白", "pulse": "脉虚无力", "formula": "养心汤", "treatment": "补益心气"},
    {"name": "心血虚证", "category": "脏腑辨证", "symptoms": "心悸失眠、多梦、头晕健忘", "tongue": "舌淡白", "pulse": "脉细弱", "formula": "四物汤", "treatment": "养血安神"},
    {"name": "心火亢盛证", "category": "脏腑辨证", "symptoms": "心烦失眠、口舌生疮、小便短赤", "tongue": "舌尖红赤", "pulse": "脉数", "formula": "导赤散", "treatment": "清心泻火"},
    {"name": "心血瘀阻证", "category": "脏腑辨证", "symptoms": "心胸憋闷疼痛、痛引肩背", "tongue": "舌紫暗有瘀斑", "pulse": "脉涩", "formula": "血府逐瘀汤", "treatment": "活血化瘀、通脉止痛"},

    # 脏腑辨证 - 肝系
    {"name": "肝气郁结证", "category": "脏腑辨证", "symptoms": "胸胁胀痛、善太息、情志抑郁", "tongue": "舌苔薄白", "pulse": "脉弦", "formula": "逍遥散", "treatment": "疏肝解郁"},
    {"name": "肝火上炎证", "category": "脏腑辨证", "symptoms": "头胀头痛、面红目赤、急躁易怒", "tongue": "舌红苔黄", "pulse": "脉弦数", "formula": "龙胆泻肝汤", "treatment": "清肝泻火"},
    {"name": "肝血虚证", "category": "脏腑辨证", "symptoms": "眩晕耳鸣、夜盲、肢体麻木", "tongue": "舌淡白", "pulse": "脉弦细", "formula": "四物汤", "treatment": "补血养肝"},
    {"name": "肝阳上亢证", "category": "脏腑辨证", "symptoms": "眩晕耳鸣、头目胀痛、腰膝酸软", "tongue": "舌红少津", "pulse": "脉弦有力", "formula": "天麻钩藤饮", "treatment": "滋阴潜阳"},

    # 脏腑辨证 - 脾系
    {"name": "脾气虚证", "category": "脏腑辨证", "symptoms": "纳少腹胀、便溏、乏力", "tongue": "舌淡苔白", "pulse": "脉缓弱", "formula": "四君子汤", "treatment": "健脾益气"},
    {"name": "脾阳虚证", "category": "脏腑辨证", "symptoms": "腹胀纳少、腹痛喜温喜按", "tongue": "舌淡胖苔白", "pulse": "脉沉迟", "formula": "理中丸", "treatment": "温中健脾"},
    {"name": "脾不统血证", "category": "脏腑辨证", "symptoms": "便血、尿血、月经过多", "tongue": "舌淡白", "pulse": "脉细弱", "formula": "归脾汤", "treatment": "补脾摄血"},
    {"name": "寒湿困脾证", "category": "脏腑辨证", "symptoms": "脘腹痞闷、便溏、头身困重", "tongue": "舌苔白腻", "pulse": "脉濡缓", "formula": "平胃散", "treatment": "温中散寒、燥湿健脾"},
    {"name": "湿热蕴脾证", "category": "脏腑辨证", "symptoms": "脘腹痞闷、便溏不爽、面目发黄", "tongue": "舌红苔黄腻", "pulse": "脉濡数", "formula": "茵陈蒿汤", "treatment": "清热利湿健脾"},

    # 脏腑辨证 - 肺系
    {"name": "肺气虚证", "category": "脏腑辨证", "symptoms": "咳喘无力、气短自汗", "tongue": "舌淡苔白", "pulse": "脉虚无力", "formula": "补肺汤", "treatment": "补益肺气"},
    {"name": "肺阴虚证", "category": "脏腑辨证", "symptoms": "干咳少痰、潮热盗汗", "tongue": "舌红少苔", "pulse": "脉细数", "formula": "百合固金汤", "treatment": "滋阴润肺"},
    {"name": "风寒犯肺证", "category": "脏腑辨证", "symptoms": "咳嗽痰稀、鼻塞流清涕", "tongue": "舌苔薄白", "pulse": "脉浮紧", "formula": "杏苏散", "treatment": "疏风散寒、宣肺止咳"},
    {"name": "风热犯肺证", "category": "脏腑辨证", "symptoms": "咳嗽痰黄、口渴咽痛", "tongue": "舌苔薄黄", "pulse": "脉浮数", "formula": "桑菊饮", "treatment": "疏风清热、宣肺止咳"},
    {"name": "痰热壅肺证", "category": "脏腑辨证", "symptoms": "咳嗽气喘、痰多黄稠", "tongue": "舌红苔黄腻", "pulse": "脉滑数", "formula": "清气化痰丸", "treatment": "清热化痰、宣肺平喘"},

    # 脏腑辨证 - 肾系
    {"name": "肾阳虚证", "category": "脏腑辨证", "symptoms": "畏寒肢冷、腰膝酸软、阳痿早泄", "tongue": "舌淡苔白", "pulse": "脉沉迟", "formula": "金匮肾气丸", "treatment": "温补肾阳"},
    {"name": "肾阴虚证", "category": "脏腑辨证", "symptoms": "腰膝酸软、头晕耳鸣、潮热盗汗", "tongue": "舌红少苔", "pulse": "脉细数", "formula": "六味地黄丸", "treatment": "滋补肾阴"},
    {"name": "肾精不足证", "category": "脏腑辨证", "symptoms": "小儿发育迟缓、成人早衰", "tongue": "舌淡", "pulse": "脉弱", "formula": "左归丸", "treatment": "补肾填精"},
    {"name": "肾不纳气证", "category": "脏腑辨证", "symptoms": "呼多吸少、动则气喘", "tongue": "舌淡苔白", "pulse": "脉沉弱", "formula": "金匮肾气丸", "treatment": "补肾纳气"},

    # 气血津液辨证
    {"name": "气虚证", "category": "气血津液辨证", "symptoms": "神疲乏力、气短懒言、自汗", "tongue": "舌淡苔白", "pulse": "脉虚无力", "formula": "四君子汤", "treatment": "补气"},
    {"name": "气陷证", "category": "气血津液辨证", "symptoms": "气短乏力、久泻脱肛、内脏下垂", "tongue": "舌淡苔白", "pulse": "脉虚无力", "formula": "补中益气汤", "treatment": "补气升阳"},
    {"name": "气滞证", "category": "气血津液辨证", "symptoms": "胀闷疼痛、走窜不定", "tongue": "舌苔薄白", "pulse": "脉弦", "formula": "柴胡疏肝散", "treatment": "行气"},
    {"name": "血虚证", "category": "气血津液辨证", "symptoms": "面色淡白、头晕心悸", "tongue": "舌淡白", "pulse": "脉细无力", "formula": "四物汤", "treatment": "补血"},
    {"name": "血瘀证", "category": "气血津液辨证", "symptoms": "刺痛固定、面色晦暗", "tongue": "舌紫暗有瘀斑", "pulse": "脉涩", "formula": "血府逐瘀汤", "treatment": "活血化瘀"},
    {"name": "痰证", "category": "气血津液辨证", "symptoms": "胸闷痰多、头晕目眩", "tongue": "舌苔白腻", "pulse": "脉滑", "formula": "二陈汤", "treatment": "化痰"},
    {"name": "饮证", "category": "气血津液辨证", "symptoms": "胸胁胀满、咳唾引痛", "tongue": "舌苔白滑", "pulse": "脉弦", "formula": "十枣汤", "treatment": "逐饮"},
    {"name": "津亏证", "category": "气血津液辨证", "symptoms": "口燥咽干、皮肤干枯、大便干结", "tongue": "舌红少津", "pulse": "脉细数", "formula": "增液汤", "treatment": "生津"},

    # 痹证
    {"name": "风寒湿痹证", "category": "痹证", "symptoms": "关节肌肉疼痛、遇寒加重", "tongue": "舌苔白腻", "pulse": "脉弦紧", "formula": "独活寄生汤", "treatment": "祛风散寒、除湿通络"},
    {"name": "风湿热痹证", "category": "痹证", "symptoms": "关节红肿热痛、发热", "tongue": "舌红苔黄腻", "pulse": "脉滑数", "formula": "白虎加桂枝汤", "treatment": "清热通络、祛风除湿"},

    # 卫气营血辨证
    {"name": "卫分证", "category": "卫气营血辨证", "symptoms": "发热微恶风寒、口微渴", "tongue": "舌边尖红", "pulse": "脉浮数", "formula": "银翘散", "treatment": "辛凉解表"},
    {"name": "气分证", "category": "卫气营血辨证", "symptoms": "壮热不恶寒、汗多渴喜冷饮", "tongue": "舌红苔黄", "pulse": "脉洪数", "formula": "白虎汤", "treatment": "清气泄热"},
    {"name": "营分证", "category": "卫气营血辨证", "symptoms": "身热夜甚、心烦不寐", "tongue": "舌红绛", "pulse": "脉细数", "formula": "清营汤", "treatment": "清营透热"},
    {"name": "血分证", "category": "卫气营血辨证", "symptoms": "身热出血、斑疹显露", "tongue": "舌深绛", "pulse": "脉细数", "formula": "犀角地黄汤", "treatment": "凉血散血"},
]

HERBS = [
    # 解表药
    {"name": "麻黄", "nature": "温", "flavor": "辛", "meridian": "肺、膀胱", "function": "发汗解表、宣肺平喘、利水消肿", "indication": "风寒感冒、风水水肿", "dosage": "2-10g", "caution": "表虚自汗、阴虚盗汗"},
    {"name": "桂枝", "nature": "温", "flavor": "辛、甘", "meridian": "心、肺、膀胱", "function": "发汗解表、温通经脉、助阳化气", "indication": "风寒感冒、寒凝血滞", "dosage": "3-10g", "caution": "血热妄行、阴虚火旺"},
    {"name": "紫苏", "nature": "温", "flavor": "辛", "meridian": "肺、脾", "function": "解表散寒、行气宽中", "indication": "风寒感冒、脾胃气滞", "dosage": "5-10g", "caution": "气虚阴虚"},
    {"name": "荆芥", "nature": "微温", "flavor": "辛", "meridian": "肺、肝", "function": "祛风解表、透疹消疮", "indication": "外感表证、麻疹不透", "dosage": "5-10g", "caution": "表虚自汗"},
    {"name": "防风", "nature": "微温", "flavor": "辛、甘", "meridian": "膀胱、肝、脾", "function": "祛风解表、胜湿止痛", "indication": "外感表证、风湿痹痛", "dosage": "5-10g", "caution": "阴血亏虚"},
    {"name": "羌活", "nature": "温", "flavor": "辛、苦", "meridian": "膀胱、肾", "function": "解表散寒、祛风胜湿、止痛", "indication": "风寒感冒、风湿痹痛", "dosage": "3-10g", "caution": "血虚痹痛"},
    {"name": "白芷", "nature": "温", "flavor": "辛", "meridian": "肺、胃、大肠", "function": "解表散寒、祛风止痛、通鼻窍", "indication": "风寒感冒、头痛牙痛", "dosage": "3-10g", "caution": "阴虚血热"},
    {"name": "细辛", "nature": "温", "flavor": "辛", "meridian": "心、肺、肾", "function": "解表散寒、祛风止痛、温肺化饮", "indication": "风寒感冒、头痛牙痛", "dosage": "1-3g", "caution": "阴虚阳亢"},
    {"name": "薄荷", "nature": "凉", "flavor": "辛", "meridian": "肺、肝", "function": "疏散风热、清利头目、利咽透疹", "indication": "风热感冒、头痛目赤", "dosage": "3-6g（后下）", "caution": "体虚多汗"},
    {"name": "牛蒡子", "nature": "寒", "flavor": "辛、苦", "meridian": "肺、胃", "function": "疏散风热、宣肺祛痰、利咽透疹", "indication": "风热感冒、咽喉肿痛", "dosage": "6-12g", "caution": "脾虚便溏"},
    {"name": "蝉蜕", "nature": "寒", "flavor": "甘", "meridian": "肺、肝", "function": "疏散风热、利咽开音、透疹、明目退翳", "indication": "风热感冒、咽痛音哑", "dosage": "3-6g", "caution": "孕妇慎用"},
    {"name": "桑叶", "nature": "寒", "flavor": "苦、甘", "meridian": "肺、肝", "function": "疏散风热、清肺润燥、平抑肝阳、清肝明目", "indication": "风热感冒、肺热燥咳", "dosage": "5-10g", "caution": "肝燥者禁用"},
    {"name": "菊花", "nature": "微寒", "flavor": "甘、苦", "meridian": "肺、肝", "function": "疏散风热、平抑肝阳、清肝明目、清热解毒", "indication": "风热感冒、头痛眩晕", "dosage": "5-10g", "caution": "气虚胃寒者少用"},

    # 清热药
    {"name": "石膏", "nature": "大寒", "flavor": "辛、甘", "meridian": "肺、胃", "function": "清热泻火、除烦止渴", "indication": "气分实热证、肺热喘咳", "dosage": "15-60g", "caution": "脾胃虚寒"},
    {"name": "知母", "nature": "寒", "flavor": "苦、甘", "meridian": "肺、胃、肾", "function": "清热泻火、滋阴润燥", "indication": "气分实热证、阴虚燥咳", "dosage": "6-12g", "caution": "脾虚便溏"},
    {"name": "栀子", "nature": "寒", "flavor": "苦", "meridian": "心、肺、三焦", "function": "泻火除烦、清热利湿、凉血解毒", "indication": "热病心烦、湿热黄疸", "dosage": "6-10g", "caution": "脾虚便溏"},
    {"name": "黄芩", "nature": "寒", "flavor": "苦", "meridian": "肺、胆、脾、大肠", "function": "清热燥湿、泻火解毒、止血安胎", "indication": "湿温暑湿、肺热咳嗽", "dosage": "3-10g", "caution": "脾胃虚寒"},
    {"name": "黄连", "nature": "寒", "flavor": "苦", "meridian": "心、脾、胃、肝、胆、大肠", "function": "清热燥湿、泻火解毒", "indication": "湿热痞满、高热神昏", "dosage": "2-5g", "caution": "脾胃虚寒"},
    {"name": "黄柏", "nature": "寒", "flavor": "苦", "meridian": "肾、膀胱、大肠", "function": "清热燥湿、泻火除蒸、解毒疗疮", "indication": "湿热泻痢、骨蒸劳热", "dosage": "6-12g", "caution": "脾胃虚寒"},
    {"name": "金银花", "nature": "寒", "flavor": "甘", "meridian": "肺、心、胃", "function": "清热解毒、疏散风热", "indication": "痈肿疔疮、外感风热", "dosage": "10-15g", "caution": "脾胃虚寒"},
    {"name": "连翘", "nature": "微寒", "flavor": "苦", "meridian": "肺、心、小肠", "function": "清热解毒、消肿散结、疏散风热", "indication": "痈肿疮毒、外感风热", "dosage": "6-15g", "caution": "脾胃虚弱"},
    {"name": "板蓝根", "name": "板蓝根", "nature": "寒", "flavor": "苦", "meridian": "心、胃", "function": "清热解毒、凉血利咽", "indication": "温疫发热、咽喉肿痛", "dosage": "10-15g", "caution": "体虚而无实火热毒者忌服"},
    {"name": "蒲公英", "nature": "寒", "flavor": "苦、甘", "meridian": "肝、胃", "function": "清热解毒、消肿散结、利尿通淋", "indication": "疔疮肿毒、乳痈、目赤", "dosage": "10-15g", "caution": "阳虚外寒者慎用"},

    # 泻下药
    {"name": "大黄", "nature": "寒", "flavor": "苦", "meridian": "脾、胃、大肠、肝", "function": "泻下攻积、清热泻火、凉血解毒", "indication": "热结便秘、血热吐衄", "dosage": "3-15g", "caution": "孕妇及月经期"},
    {"name": "芒硝", "nature": "寒", "flavor": "咸、苦", "meridian": "胃、大肠", "function": "泻下通便、润燥软坚、清热消肿", "indication": "实热积滞、大便燥结", "dosage": "6-12g（冲服）", "caution": "孕妇及哺乳期"},
    {"name": "火麻仁", "nature": "平", "flavor": "甘", "meridian": "脾、胃、大肠", "function": "润肠通便", "indication": "血虚津亏便秘", "dosage": "10-15g", "caution": "大便溏泄者忌服"},

    # 祛风湿药
    {"name": "独活", "nature": "微温", "flavor": "辛、苦", "meridian": "肾、膀胱", "function": "祛风湿、止痛、解表", "indication": "风湿痹痛、风寒表证", "dosage": "3-10g", "caution": "阴虚血燥者慎服"},
    {"name": "威灵仙", "nature": "温", "flavor": "辛、咸", "meridian": "膀胱", "function": "祛风湿、通络止痛、消骨鲠", "indication": "风湿痹痛、肢体麻木", "dosage": "6-10g", "caution": "气血虚弱者慎服"},
    {"name": "秦艽", "nature": "平", "flavor": "辛、苦", "meridian": "胃、肝、胆", "function": "祛风湿、通络止痛、退虚热、清湿热", "indication": "风湿痹痛、骨蒸潮热", "dosage": "3-10g", "caution": "久痛虚羸者慎用"},

    # 化湿药
    {"name": "藿香", "nature": "微温", "flavor": "辛", "meridian": "脾、胃、肺", "function": "芳香化湿、和中止呕、发表解暑", "indication": "湿阻中焦、呕吐、暑湿表证", "dosage": "3-10g", "caution": "阴虚火旺者忌服"},
    {"name": "苍术", "nature": "温", "flavor": "辛、苦", "meridian": "脾、胃、肝", "function": "燥湿健脾、祛风散寒", "indication": "湿盛困脾、风湿痹痛", "dosage": "3-9g", "caution": "阴虚内热、气虚多汗"},
    {"name": "厚朴", "nature": "温", "flavor": "苦、辛", "meridian": "脾、胃、肺、大肠", "function": "燥湿消痰、下气除满", "indication": "湿滞伤中、脘腹胀满", "dosage": "3-9g", "caution": "气虚津亏"},
    {"name": "砂仁", "nature": "温", "flavor": "辛", "meridian": "脾、胃、肾", "function": "化湿开胃、温脾止泻、理气安胎", "indication": "湿阻中焦、脾胃气滞", "dosage": "3-6g（后下）", "caution": "阴虚有热者忌服"},

    # 利水渗湿药
    {"name": "茯苓", "nature": "平", "flavor": "甘、淡", "meridian": "心、肺、脾、肾", "function": "利水渗湿、健脾宁心", "indication": "水肿尿少、脾虚食少", "dosage": "9-15g", "caution": "虚寒精滑"},
    {"name": "猪苓", "nature": "平", "flavor": "甘、淡", "meridian": "肾、膀胱", "function": "利水渗湿", "indication": "小便不利、水肿", "dosage": "6-12g", "caution": "无水湿者"},
    {"name": "泽泻", "nature": "寒", "flavor": "甘、淡", "meridian": "肾、膀胱", "function": "利水渗湿、泄热", "indication": "水肿胀满、痰饮眩晕", "dosage": "6-10g", "caution": "肾虚精滑"},
    {"name": "薏苡仁", "nature": "凉", "flavor": "甘、淡", "meridian": "脾、胃、肺", "function": "利水渗湿、健脾止泻、除痹排脓", "indication": "水肿、脾虚泄泻", "dosage": "9-30g", "caution": "津液不足"},
    {"name": "车前子", "nature": "寒", "flavor": "甘", "meridian": "肝、肾、肺、小肠", "function": "清热利尿、渗湿止泻、明目、祛痰", "indication": "水肿胀满、暑湿泄泻", "dosage": "9-15g", "caution": "肾虚精滑者忌服"},

    # 温里药
    {"name": "附子", "nature": "大热", "flavor": "辛、甘", "meridian": "心、肾、脾", "function": "回阳救逆、补火助阳、散寒止痛", "indication": "亡阳证、阳虚诸证", "dosage": "3-15g（先煎）", "caution": "孕妇及阴虚阳亢"},
    {"name": "干姜", "nature": "热", "flavor": "辛", "meridian": "脾、胃、心、肺", "function": "温中散寒、回阳通脉、温肺化饮", "indication": "脾胃寒证、亡阳证", "dosage": "3-10g", "caution": "阴虚内热"},
    {"name": "肉桂", "nature": "大热", "flavor": "辛、甘", "meridian": "肾、脾、心、肝", "function": "补火助阳、引火归元、散寒止痛", "indication": "阳痿宫冷、腰膝冷痛", "dosage": "2-5g（后下）", "caution": "阴虚火旺"},
    {"name": "吴茱萸", "nature": "热", "flavor": "辛、苦", "meridian": "肝、脾、胃、肾", "function": "散寒止痛、降逆止呕、温中止泻", "indication": "厥阴头痛、寒疝腹痛", "dosage": "1.5-4.5g", "caution": "阴虚有热"},

    # 理气药
    {"name": "陈皮", "nature": "温", "flavor": "辛、苦", "meridian": "脾、肺", "function": "理气健脾、燥湿化痰", "indication": "脘腹胀满、咳嗽痰多", "dosage": "3-10g", "caution": "气虚证"},
    {"name": "枳实", "nature": "微寒", "flavor": "苦、辛", "meridian": "脾、胃、大肠", "function": "破气消积、化痰散痞", "indication": "食积气滞、痰滞胸脘", "dosage": "3-10g", "caution": "脾胃虚弱"},
    {"name": "木香", "nature": "温", "flavor": "辛、苦", "meridian": "脾、胃、大肠、三焦、胆", "function": "行气止痛、健脾消食", "indication": "脾胃气滞、泻痢后重", "dosage": "1.5-6g", "caution": "阴虚津亏"},
    {"name": "香附", "nature": "平", "flavor": "辛、微苦", "meridian": "肝、脾、三焦", "function": "疏肝理气、调经止痛", "indication": "肝郁气滞、月经不调", "dosage": "6-10g", "caution": "气虚胀满"},
    {"name": "薤白", "nature": "温", "flavor": "辛、苦", "meridian": "心、肺、胃、大肠", "function": "通阳散结、行气导滞", "indication": "胸痹证：胸闷心痛", "dosage": "5-10g", "caution": "气虚无滞者忌服"},

    # 消食药
    {"name": "山楂", "nature": "微温", "flavor": "酸、甘", "meridian": "脾、胃、肝", "function": "消食化积、行气散瘀", "indication": "肉食积滞、产后瘀阻", "dosage": "9-12g", "caution": "脾胃虚弱无积滞者慎用"},
    {"name": "神曲", "nature": "温", "flavor": "辛、甘", "meridian": "脾、胃", "function": "消食和胃", "indication": "饮食积滞", "dosage": "6-12g", "caution": "胃阴虚、胃火盛者不宜用"},
    {"name": "麦芽", "nature": "平", "flavor": "甘", "meridian": "脾、胃、肝", "function": "消食健胃、回乳消胀", "indication": "米面薯芋食滞、断乳", "dosage": "10-15g", "caution": "哺乳期妇女不宜用"},
    {"name": "莱菔子", "nature": "平", "flavor": "辛、甘", "meridian": "脾、胃、肺", "function": "消食除胀、降气化痰", "indication": "食积气滞、咳喘痰多", "dosage": "6-10g", "caution": "气虚及无食积者慎用"},

    # 止血药
    {"name": "小蓟", "nature": "凉", "flavor": "甘、苦", "meridian": "心、肝", "function": "凉血止血、散瘀解毒消痈", "indication": "血热出血、痈肿疮毒", "dosage": "10-15g", "caution": "脾胃虚寒者慎用"},
    {"name": "地榆", "nature": "微寒", "flavor": "苦、酸", "meridian": "肝、大肠", "function": "凉血止血、解毒敛疮", "indication": "血热出血、烫伤湿疹", "dosage": "10-15g", "caution": "大面积烧伤者不宜使用"},
    {"name": "白茅根", "nature": "寒", "flavor": "甘", "meridian": "肺、胃、膀胱", "function": "凉血止血、清热利尿", "indication": "血热出血、水肿尿少", "dosage": "9-30g", "caution": "脾胃虚寒者慎用"},

    # 活血化瘀药
    {"name": "川芎", "nature": "温", "flavor": "辛", "meridian": "肝、胆、心包", "function": "活血行气、祛风止痛", "indication": "血瘀诸证、风湿痹痛", "dosage": "3-10g", "caution": "出血性疾病"},
    {"name": "丹参", "nature": "微寒", "flavor": "苦", "meridian": "心、肝", "function": "活血祛瘀、通经止痛、凉血消痈", "indication": "月经不调、血瘀心痛", "dosage": "5-15g", "caution": "孕妇"},
    {"name": "桃仁", "nature": "平", "flavor": "苦、甘", "meridian": "心、肝、大肠", "function": "活血祛瘀、润肠通便", "indication": "血瘀诸证、肠燥便秘", "dosage": "5-10g", "caution": "孕妇"},
    {"name": "红花", "nature": "温", "flavor": "辛", "meridian": "心、肝", "function": "活血通经、祛瘀止痛", "indication": "血瘀痛经、跌打损伤", "dosage": "3-9g", "caution": "孕妇"},
    {"name": "益母草", "nature": "微寒", "flavor": "辛、苦", "meridian": "心、肝、膀胱", "function": "活血调经、利尿消肿、清热解毒", "indication": "月经不调、水肿尿少", "dosage": "9-30g", "caution": "孕妇禁用"},
    {"name": "牛膝", "nature": "平", "flavor": "苦、甘、酸", "meridian": "肝、肾", "function": "逐瘀通经、补肝肾、强筋骨、利尿通淋", "indication": "血瘀诸证、腰膝酸软", "dosage": "5-12g", "caution": "孕妇及月经过多"},

    # 化痰止咳平喘药
    {"name": "半夏", "nature": "温", "flavor": "辛", "meridian": "脾、胃、肺", "function": "燥湿化痰、降逆止呕、消痞散结", "indication": "痰多咳喘、呕吐反胃", "dosage": "3-10g", "caution": "阴虚燥咳"},
    {"name": "天南星", "nature": "温", "flavor": "苦、辛", "meridian": "肺、肝、脾", "function": "燥湿化痰、祛风止痉", "indication": "顽痰咳嗽、风痰眩晕", "dosage": "3-9g", "caution": "孕妇慎用"},
    {"name": "桔梗", "nature": "平", "flavor": "苦、辛", "meridian": "肺", "function": "宣肺、利咽、祛痰、排脓", "indication": "咳嗽痰多、咽喉肿痛", "dosage": "3-10g", "caution": "气机上逆者忌用"},
    {"name": "川贝母", "nature": "微寒", "flavor": "苦、甘", "meridian": "肺、心", "function": "清热润肺、化痰止咳", "indication": "肺热燥咳、干咳少痰", "dosage": "3-10g", "caution": "脾胃虚寒者慎用"},
    {"name": "杏仁", "nature": "微温", "flavor": "苦", "meridian": "肺、大肠", "function": "止咳平喘、润肠通便", "indication": "咳嗽气喘、肠燥便秘", "dosage": "5-10g（打碎）", "caution": "婴幼儿慎用"},

    # 安神药
    {"name": "酸枣仁", "nature": "平", "flavor": "甘、酸", "meridian": "心、肝、胆", "function": "养心补肝、宁心安神、敛汗生津", "indication": "虚烦不眠、惊悸多梦", "dosage": "9-15g", "caution": "有实邪郁火者慎用"},
    {"name": "远志", "nature": "温", "flavor": "苦、辛", "meridian": "心、肾、肺", "function": "安神益智、祛痰消肿", "indication": "失眠多梦、健忘惊悸", "dosage": "3-10g", "caution": "胃炎及溃疡者慎用"},
    {"name": "柏子仁", "nature": "平", "flavor": "甘", "meridian": "心、肾、大肠", "function": "养心安神、润肠通便", "indication": "心悸失眠、肠燥便秘", "dosage": "6-12g", "caution": "便溏者慎用"},

    # 平肝息风药
    {"name": "天麻", "nature": "平", "flavor": "甘", "meridian": "肝", "function": "息风止痉、平抑肝阳、祛风通络", "indication": "头痛眩晕、肢体麻木", "dosage": "3-10g", "caution": "气血虚弱"},
    {"name": "钩藤", "nature": "微寒", "flavor": "甘", "meridian": "肝、心包", "function": "清热平肝、息风定惊", "indication": "头痛眩晕、惊痫抽搐", "dosage": "3-12g（后下）", "caution": "无风热实火者慎用"},
    {"name": "石决明", "nature": "寒", "flavor": "咸", "meridian": "肝", "function": "平肝潜阳、清肝明目", "indication": "头痛眩晕、目赤翳障", "dosage": "9-30g（先煎）", "caution": "脾胃虚寒者慎用"},

    # 补虚药
    {"name": "人参", "nature": "微温", "flavor": "甘、微苦", "meridian": "脾、肺、心、肾", "function": "大补元气、复脉固脱、补脾益肺", "indication": "气虚欲脱、脾肺气虚", "dosage": "3-9g（另煎）", "caution": "实证热证"},
    {"name": "黄芪", "nature": "微温", "flavor": "甘", "meridian": "脾、肺", "function": "补气升阳、固表止痛、利水消肿", "indication": "气虚乏力、久泻脱肛", "dosage": "9-30g", "caution": "表实邪盛"},
    {"name": "白术", "nature": "温", "flavor": "苦、甘", "meridian": "脾、胃", "function": "健脾益气、燥湿利水、止汗安胎", "indication": "脾虚食少、痰饮眩悸", "dosage": "6-12g", "caution": "阴虚燥渴"},
    {"name": "甘草", "nature": "平", "flavor": "甘", "meridian": "心、肺、脾、胃", "function": "补脾益气、清热解毒、调和诸药", "indication": "脾胃虚弱、咳嗽痰多", "dosage": "2-10g", "caution": "湿盛胀满"},
    {"name": "当归", "nature": "温", "flavor": "甘、辛", "meridian": "肝、心、脾", "function": "补血活血、调经止痛、润肠通便", "indication": "血虚诸证、月经不调", "dosage": "6-12g", "caution": "湿盛中满"},
    {"name": "熟地黄", "nature": "微温", "flavor": "甘", "meridian": "肝、肾", "function": "补血滋阴、益精填髓", "indication": "血虚诸证、肝肾阴虚", "dosage": "9-15g", "caution": "脾胃虚弱"},
    {"name": "白芍", "nature": "微寒", "flavor": "苦、酸", "meridian": "肝、脾", "function": "养血敛阴、柔肝止痛、平抑肝阳", "indication": "血虚诸证、肝郁胁痛", "dosage": "6-15g", "caution": "虚寒腹泻"},
    {"name": "阿胶", "nature": "平", "flavor": "甘", "meridian": "肺、肝、肾", "function": "补血滋阴、润燥止血", "indication": "血虚萎黄、眩晕心悸", "dosage": "3-9g（烊化）", "caution": "脾胃虚弱者慎用"},
    {"name": "枸杞子", "nature": "平", "flavor": "甘", "meridian": "肝、肾", "function": "滋补肝肾、益精明目", "indication": "肝肾阴虚、目昏不明", "dosage": "6-12g", "caution": "脾虚有湿及泄泻者忌服"},
    {"name": "何首乌", "nature": "微温", "flavor": "苦、甘、涩", "meridian": "肝、肾", "function": "补益精血、固肾乌须", "indication": "精血亏虚、须发早白", "dosage": "6-12g", "caution": "大便溏泄及有痰湿者慎用"},

    # 收涩药
    {"name": "五味子", "nature": "温", "flavor": "酸、甘", "meridian": "肺、心、肾", "function": "收敛固涩、益气生津、补肾宁心", "indication": "久嗽虚喘、自汗盗汗", "dosage": "2-6g", "caution": "表邪未解者慎用"},
    {"name": "山茱萸", "nature": "微温", "flavor": "酸、涩", "meridian": "肝、肾", "function": "补益肝肾、收涩固脱", "indication": "眩晕耳鸣、腰膝酸痛", "dosage": "6-12g", "caution": "命门火炽者忌服"},
    {"name": "莲子", "nature": "平", "flavor": "甘、涩", "meridian": "脾、肾、心", "function": "补脾止泻、止带、益肾涩精、养心安神", "indication": "脾虚泄泻、带下、遗精", "dosage": "9-15g", "caution": "中满痞胀者忌服"},

    # 其他
    {"name": "柴胡", "nature": "微寒", "flavor": "苦、辛", "meridian": "肝、胆、肺", "function": "和解表里、疏肝升阳、退热截疟", "indication": "感冒发热、肝郁气滞", "dosage": "3-10g", "caution": "肝阳上亢"},
    {"name": "升麻", "nature": "微寒", "flavor": "辛、微甘", "meridian": "肺、脾、胃、大肠", "function": "解表透疹、清热解毒、升举阳气", "indication": "风热感冒、麻疹不透、久泻脱肛", "dosage": "3-10g", "caution": "阴虚火旺者忌用"},
    {"name": "葛根", "nature": "凉", "flavor": "甘、辛", "meridian": "脾、胃、肺", "function": "解肌退热、透疹、生津止渴、升阳止泻", "indication": "表证发热、项背强痛", "dosage": "9-15g", "caution": "胃寒呕吐者慎用"},
]
