import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os


# 分词处理
def tokenize(text):
    return " ".join(jieba.lcut(text))


FIRE_KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "static", "fire_knowledge_base.txt"
)


# 场景判别
# TF-IDF算法：sklearn + jieba分词库实现
def judgement_scene(text):
    with open(FIRE_KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        fire_knowledge_base = f.read()

    # 1. 定义行业标杆数据 (每个行业建议合并多篇文章)
    training_data = {
        "消防救援": fire_knowledge_base,
        "金融财政": "中央银行调整存款准备金率，影响市场流动性，证券公司分析营收和净利润增长。",
        "政府要文": "各级部门要深入贯彻落实相关指导思想，加强制度建设，推动高质量发展，服务基层群众。",
    }
    # 准备训练集
    labels = list(training_data.keys())
    corpus = [tokenize(txt) for txt in training_data.values()]

    # 3. 初始化并 Fit（构建特征空间）
    # max_df=0.8 表示如果一个词在80%的文档都出现（如“的”），则剔除
    vectorizer = TfidfVectorizer(max_df=0.8)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # 4. 判别新文本
    new_vec = vectorizer.transform([tokenize(text)])

    # 5. 计算相似度并输出
    scores = cosine_similarity(new_vec, tfidf_matrix)[0]

    print("--- 场景判别结果 ---")
    for i, score in enumerate(scores):
        print(f"场景【{labels[i]}】匹配得分: {score:.4f}")

    result = labels[scores.argmax()]
    print(f"\n最终判定: 该文本属于【{result}】")
    return result
