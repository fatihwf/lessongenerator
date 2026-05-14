"""
Bloom-aware Personalized Lesson Generator — FastAPI application entry point.

Mounts all routers under /api to match the reverse proxy path prefix.
Initializes DB tables on startup and seeds example data if tables are empty.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, SessionLocal
from logger import logger
from routes.health import router as health_router
from routes.curriculum import router as curriculum_router
from routes.profiles import router as profiles_router
from routes.bloom_routes import router as bloom_router
from routes.rag_routes import router as rag_router
from routes.lessons import router as lessons_router
from routes.feedback import router as feedback_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: init DB and seed on startup."""
    logger.info("startup.begin")
    init_db()
    _seed_if_empty()
    logger.info("startup.done")
    yield
    logger.info("shutdown.begin")


def _seed_if_empty():
    """Seed minimal example data so the app isn't empty on first load."""
    from models import CurriculumItem, LearnerProfile, KnowledgeChunk
    from datetime import datetime

    db = SessionLocal()
    try:
        if db.query(LearnerProfile).count() > 0:
            return

        logger.info("seed.start")

        profiles = [
            LearnerProfile(
                name="Ayşe Kaya",
                grade="7",
                proficiency_level="intermediate",
                reading_level="grade_level",
                preferred_style="visual",
                weak_topics=["fractions", "geometry"],
                strong_topics=["algebra", "arithmetic"],
                created_at=datetime.utcnow(),
            ),
            LearnerProfile(
                name="Mehmet Yılmaz",
                grade="8",
                proficiency_level="advanced",
                reading_level="above_grade",
                preferred_style="analytical",
                weak_topics=["probability"],
                strong_topics=["equations", "functions"],
                created_at=datetime.utcnow(),
            ),
            LearnerProfile(
                name="Zeynep Arslan",
                grade="6",
                proficiency_level="beginner",
                reading_level="below_grade",
                preferred_style="hands_on",
                weak_topics=["multiplication", "division"],
                strong_topics=["addition", "subtraction"],
                created_at=datetime.utcnow(),
            ),
        ]
        db.add_all(profiles)
        db.flush()

        outcomes = [
            CurriculumItem(
                subject="Matematik",
                grade="7",
                unit="Kesirler",
                outcome_text="Öğrenci kesirleri karşılaştırabilir ve sıralayabilir.",
                bloom_level="understanding",
                secondary_bloom_levels=["analyzing"],
                bloom_confidence=0.82,
                created_at=datetime.utcnow(),
            ),
            CurriculumItem(
                subject="Matematik",
                grade="8",
                unit="Denklemler",
                outcome_text="Birinci dereceden denklemleri çözebilir ve sonuçları yorumlayabilir.",
                bloom_level="applying",
                secondary_bloom_levels=["understanding"],
                bloom_confidence=0.88,
                created_at=datetime.utcnow(),
            ),
            CurriculumItem(
                subject="Fen Bilimleri",
                grade="7",
                unit="Hücre",
                outcome_text="Hayvan ve bitki hücrelerinin yapılarını karşılaştırabilir.",
                bloom_level="analyzing",
                secondary_bloom_levels=["understanding"],
                bloom_confidence=0.79,
                created_at=datetime.utcnow(),
            ),
            CurriculumItem(
                subject="Türkçe",
                grade="6",
                unit="Hikaye",
                outcome_text="Okuduğu hikayedeki ana fikri ve yardımcı fikirleri belirleyebilir.",
                bloom_level="understanding",
                secondary_bloom_levels=["analyzing"],
                bloom_confidence=0.85,
                created_at=datetime.utcnow(),
            ),
        ]
        db.add_all(outcomes)
        db.flush()

        chunks = [
            KnowledgeChunk(
                content=(
                    "Kesirler, bir bütünün eşit parçalarını ifade eder. "
                    "Pay, kesrin üst kısmıdır; payda ise alt kısmıdır. "
                    "Kesirleri karşılaştırmak için ortak payda bulmak gerekir. "
                    "Örneğin 1/2 ile 1/3 karşılaştırılırken 6/6'ya dönüştürülür: "
                    "1/2 = 3/6 ve 1/3 = 2/6, dolayısıyla 1/2 > 1/3."
                ),
                source_type="MEB Ders Kitabı",
                subject="Matematik",
                grade="7",
                unit="Kesirler",
                bloom_levels=["remembering", "understanding"],
                source_name="7. Sınıf Matematik Ders Kitabı",
                created_at=datetime.utcnow(),
            ),
            KnowledgeChunk(
                content=(
                    "Birinci dereceden denklemlerde amaç bilinmeyeni bulmaktır. "
                    "Her iki tarafa aynı işlemi uygulayarak denklemi basitleştiririz. "
                    "Örnek: 2x + 3 = 11 → 2x = 8 → x = 4. "
                    "Sonuç yerine koyarak kontrol edilmelidir: 2(4) + 3 = 11. ✓"
                ),
                source_type="Öğretmen Notu",
                subject="Matematik",
                grade="8",
                unit="Denklemler",
                bloom_levels=["understanding", "applying"],
                source_name="8. Sınıf Denklemler Özet",
                created_at=datetime.utcnow(),
            ),
            KnowledgeChunk(
                content=(
                    "Hayvan hücresi: hücre zarı, sitoplazma, çekirdek, mitokondri, ribozom. "
                    "Bitki hücresi: bunlara ek olarak hücre duvarı, kloroplast ve büyük koful bulunur. "
                    "Kloroplast fotosentez için gereklidir; bu nedenle sadece bitki hücrelerinde bulunur. "
                    "Hücre duvarı bitkiye sertlik ve şekil kazandırır."
                ),
                source_type="MEB Ders Kitabı",
                subject="Fen Bilimleri",
                grade="7",
                unit="Hücre",
                bloom_levels=["remembering", "analyzing"],
                source_name="7. Sınıf Fen Bilimleri Kitabı",
                created_at=datetime.utcnow(),
            ),
            KnowledgeChunk(
                content=(
                    "Ana fikir, bir metnin en temel mesajıdır. "
                    "Yardımcı fikirler ise ana fikri destekleyen ve açıklayan ayrıntılardır. "
                    "Ana fikri bulmak için 'Bu metin bize ne anlatmak istiyor?' sorusu sorulur. "
                    "Yardımcı fikirler her paragrafta gizlidir."
                ),
                source_type="Etkinlik Föyü",
                subject="Türkçe",
                grade="6",
                unit="Hikaye",
                bloom_levels=["understanding", "analyzing"],
                source_name="6. Sınıf Türkçe Etkinlik Kitabı",
                created_at=datetime.utcnow(),
            ),
        ]
        db.add_all(chunks)
        db.commit()
        logger.info("seed.done", profiles=len(profiles), outcomes=len(outcomes), chunks=len(chunks))

    except Exception as e:
        db.rollback()
        logger.error("seed.error", error=str(e))
    finally:
        db.close()


app = FastAPI(
    title="Bloom-aware Personalized Lesson Generator",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(curriculum_router, prefix="/api")
app.include_router(profiles_router, prefix="/api")
app.include_router(bloom_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
app.include_router(lessons_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
