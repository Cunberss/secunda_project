from sqlalchemy import create_engine, text
from src.core.config import settings


def install_postgis_sync():
    # Используйте синхронный URL (без +asyncpg)
    database_url = settings.sync_database_url

    engine = create_engine(database_url)

    try:
        with engine.connect() as conn:
            # Проверяем есть ли PostGIS
            result = conn.execute(text("""
                SELECT extname FROM pg_extension WHERE extname = 'postgis'
            """))
            if result.fetchone():
                print("✅ PostGIS уже установлен")
                return True

            # Устанавливаем PostGIS
            conn.execute(text("CREATE EXTENSION postgis"))
            conn.commit()
            print("✅ PostGIS расширение установлено")

            # Проверяем тип geometry
            result = conn.execute(text("SELECT typname FROM pg_type WHERE typname = 'geometry'"))
            if result.fetchone():
                print("✅ Тип geometry доступен")
            return True

    except Exception as e:
        print(f"❌ Ошибка установки PostGIS: {e}")
        return False


if __name__ == "__main__":
    install_postgis_sync()
