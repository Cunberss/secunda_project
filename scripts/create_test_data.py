import asyncio
import random
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.core.database import async_session_maker
from src.models import Building, Organization, Activity
from src.models.organization import org_activity


class TestDataGenerator:
    def __init__(self):
        self.cities = [
            {"name": "Москва", "lat_range": (55.5, 55.9), "lon_range": (37.3, 37.9)},
            {"name": "Санкт-Петербург", "lat_range": (59.8, 60.1), "lon_range": (30.1, 30.5)},
            {"name": "Екатеринбург", "lat_range": (56.7, 56.9), "lon_range": (60.5, 60.7)},
            {"name": "Новосибирск", "lat_range": (54.9, 55.1), "lon_range": (82.8, 83.1)},
            {"name": "Казань", "lat_range": (55.7, 55.9), "lon_range": (48.9, 49.3)},
        ]

        self.streets = [
            "Ленина", "Мира", "Советская", "Центральная", "Молодежная",
            "Школьная", "Садовоя", "Парковая", "Речная", "Лесная",
            "Строителей", "Космонавтов", "Гагарина", "Кирова", "Пушкина",
            "Горького", "Чехова", "Толстого", "Достоевского", "Гоголя"
        ]

        self.building_types = ["д.", "дом", "строение", "корпус"]

        self.organization_types = [
            "ООО", "ЗАО", "ОАО", "ПАО", "ИП", "АО", "НКО"
        ]

        self.organization_names_part1 = [
            "Северный", "Южный", "Восточный", "Западный", "Центральный",
            "Городской", "Областной", "Федеральный", "Международный", "Национальный",
            "Столичный", "Региональный", "Муниципальный", "Частный", "Государственный"
        ]

        self.organization_names_part2 = [
            "Торговый", "Промышленный", "Строительный", "Финансовый", "Инвестиционный",
            "Технологический", "Научный", "Медицинский", "Образовательный", "Культурный",
            "Спортивный", "Развлекательный", "Производственный", "Логистический", "Сервисный"
        ]

        self.organization_names_part3 = [
            "Центр", "Комплекс", "Холдинг", "Альянс", "Концерн",
            "Корпорация", "Группа", "Комбинат", "Завод", "Фабрика",
            "Компания", "Предприятие", "Объединение", "Трест", "Синдикат"
        ]

        self.activity_categories = {
            "retail": [
                "Продуктовый магазин", "Одежда и обувь", "Электроника", "Мебель",
                "Строительные материалы", "Книжный магазин", "Спортивные товары",
                "Ювелирный магазин", "Цветочный магазин", "Детские товары"
            ],
            "services": [
                "Банк", "Страховая компания", "Юридические услуги", "Бухгалтерские услуги",
                "Ремонт техники", "Химчистка", "Парикмахерская", "Салон красоты",
                "Фитнес-центр", "Медицинский центр"
            ],
            "food": [
                "Ресторан", "Кафе", "Столовая", "Бар", "Пиццерия",
                "Суши-бар", "Кофейня", "Пекарня", "Кондитерская", "Фаст-фуд"
            ],
            "education": [
                "Школа", "Детский сад", "Учебный центр", "Языковая школа",
                "Музыкальная школа", "Художественная школа", "Курсы программирования",
                "Бизнес-школа", "Техникум", "Колледж"
            ],
            "entertainment": [
                "Кинотеатр", "Театр", "Боулинг", "Бильярдный клуб", "Караоке-бар",
                "Ночной клуб", "Концертный зал", "Выставочный центр", "Музей", "Галерея"
            ]
        }

        self.phone_codes = ["495", "499", "812", "343", "383", "843", "861", "862", "863", "865"]

    def generate_address(self, city_data: dict) -> str:
        """Генерация случайного адреса"""
        city = city_data["name"]
        street = random.choice(self.streets)
        building_number = random.randint(1, 200)
        building_type = random.choice(self.building_types)

        if random.random() < 0.3:
            return f"г. {city}, ул. {street}, {building_type} {building_number}"
        else:
            return f"г. {city}, ул. {street}, {building_number}"

    def generate_coordinates(self, city_data: dict) -> tuple[float, float]:
        """Генерация случайных координат в пределах города"""
        lat_range = city_data["lat_range"]
        lon_range = city_data["lon_range"]

        latitude = round(random.uniform(lat_range[0], lat_range[1]), 6)
        longitude = round(random.uniform(lon_range[0], lon_range[1]), 6)

        return latitude, longitude

    def generate_organization_name(self) -> str:
        """Генерация случайного названия организации"""
        org_type = random.choice(self.organization_types)
        part1 = random.choice(self.organization_names_part1)
        part2 = random.choice(self.organization_names_part2)
        part3 = random.choice(self.organization_names_part3)

        return f"{org_type} '{part1} {part2} {part3}'"

    def generate_phones(self, count: int = 3) -> list[str]:
        """Генерация случайных телефонных номеров"""
        phones = []
        for _ in range(count):
            code = random.choice(self.phone_codes)
            number = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
            phones.append(f"+7 ({code}) {number}")
        return phones

    def generate_activities_hierarchy(self) -> list[Activity]:
        """Генерация иерархии видов деятельности"""
        activities = []

        # Создаем родительские категории
        parent_activities = []
        for category_name, sub_activities in self.activity_categories.items():
            parent_activity = Activity(
                name=category_name.capitalize()
            )
            parent_activities.append(parent_activity)
            activities.append(parent_activity)

            # Создаем дочерние активности
            for activity_name in sub_activities:
                child_activity = Activity(
                    name=activity_name,
                    parent=parent_activity
                )
                activities.append(child_activity)

        return activities

    async def create_activities(self, session: AsyncSession) -> list[Activity]:
        """Создание видов деятельности в базе данных"""
        print("Создание видов деятельности...")

        activities = self.generate_activities_hierarchy()
        session.add_all(activities)
        await session.commit()

        # Обновляем объекты чтобы получить их ID
        for activity in activities:
            await session.refresh(activity)

        print(f"Создано {len(activities)} видов деятельности")
        return activities

    async def create_buildings(self, session: AsyncSession, count: int = 1000) -> list[Building]:
        """Создание зданий в базе данных"""
        print(f"Создание {count} зданий...")

        buildings = []
        for i in range(count):
            city_data = random.choice(self.cities)
            address = self.generate_address(city_data)
            latitude, longitude = self.generate_coordinates(city_data)

            # Создаем WKT для геометрии
            wkt_point = f"POINT({longitude} {latitude})"

            building = Building(
                address=address,
                latitude=latitude,
                longitude=longitude,
                geom=wkt_point
            )
            buildings.append(building)

            if (i + 1) % 100 == 0:
                print(f"Создано {i + 1} зданий...")

        session.add_all(buildings)
        await session.commit()

        # Обновляем объекты чтобы получить их ID
        for building in buildings:
            await session.refresh(building)

        print(f"Создано {len(buildings)} зданий")
        return buildings

    async def create_organizations(self, session: AsyncSession, buildings: list[Building],
                                   activities: list[Activity], count: int = 5000) -> list[Organization]:
        """Создание организаций в базе данных"""
        print(f"Создание {count} организаций...")

        # Фильтруем только дочерние активности (без родительских категорий)
        child_activities = [activity for activity in activities if activity.parent_id is not None]

        organizations = []
        for i in range(count):
            name = self.generate_organization_name()
            phones = self.generate_phones(random.randint(1, 3))
            building = random.choice(buildings)

            # Выбираем случайные виды деятельности (1-3 штуки)
            org_activities = random.sample(child_activities, random.randint(1, 3))

            organization = Organization(
                name=name,
                phones=phones,
                building_id=building.id,
                activities=org_activities
            )
            organizations.append(organization)

            if (i + 1) % 500 == 0:
                print(f"Создано {i + 1} организаций...")

        session.add_all(organizations)
        await session.commit()

        # Обновляем объекты чтобы получить их ID
        for organization in organizations:
            await session.refresh(organization)

        print(f"Создано {len(organizations)} организаций")
        return organizations

    async def generate_test_data(self, building_count: int = 1000, organization_count: int = 5000):
        """Основная функция генерации тестовых данных"""
        print("Начало генерации тестовых данных...")
        start_time = datetime.now()

        # ЗАМЕНА: используем async_session_maker вместо get_session()
        async with async_session_maker() as session:
            try:
                # Создаем виды деятельности
                activities = await self.create_activities(session)

                # Создаем здания
                buildings = await self.create_buildings(session, building_count)

                # Создаем организации
                organizations = await self.create_organizations(
                    session, buildings, activities, organization_count
                )

                # Выводим статистику
                await self.print_statistics(session)

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                print(f"\n✅ Генерация тестовых данных завершена!")
                print(f"⏱️  Время выполнения: {duration:.2f} секунд")

            except Exception as e:
                await session.rollback()
                print(f"❌ Ошибка при генерации тестовых данных: {e}")
                raise

    async def print_statistics(self, session: AsyncSession):
        """Вывод статистики по созданным данным"""
        print("\n📊 Статистика созданных данных:")

        # Количество зданий
        result = await session.execute(select(Building))
        buildings_count = len(result.scalars().all())
        print(f"🏢 Здания: {buildings_count}")

        # Количество организаций
        result = await session.execute(select(Organization))
        organizations_count = len(result.scalars().all())
        print(f"🏭 Организации: {organizations_count}")

        # Количество видов деятельности
        result = await session.execute(select(Activity))
        activities_count = len(result.scalars().all())
        print(f"🎯 Виды деятельности: {activities_count}")

        # Количество связей организация-деятельность
        from sqlalchemy import text
        result = await session.execute(text("SELECT COUNT(*) FROM org_activity"))
        org_activity_count = result.scalar()
        print(f"🔗 Связи организация-деятельность: {org_activity_count}")

        # Распределение организаций по городам
        result = await session.execute(text("""
            SELECT 
                CASE 
                    WHEN b.address LIKE '%Москва%' THEN 'Москва'
                    WHEN b.address LIKE '%Санкт-Петербург%' THEN 'Санкт-Петербург'
                    WHEN b.address LIKE '%Екатеринбург%' THEN 'Екатеринбург'
                    WHEN b.address LIKE '%Новосибирск%' THEN 'Новосибирск'
                    WHEN b.address LIKE '%Казань%' THEN 'Казань'
                    ELSE 'Другие'
                END as city,
                COUNT(*) as org_count
            FROM organizations o
            JOIN buildings b ON o.building_id = b.id
            GROUP BY city
            ORDER BY org_count DESC
        """))

        print("\n🏙️  Распределение организаций по городам:")
        for row in result:
            print(f"  {row.city}: {row.org_count} организаций")


async def clear_database():
    """Удаляет все данные из таблиц (в правильном порядке)."""
    async with async_session_maker() as session:
        await session.execute(delete(org_activity))
        await session.execute(delete(Organization))
        await session.execute(delete(Activity))
        await session.execute(delete(Building))
        await session.commit()
        print("✅ База очищена.")


async def main():
    await clear_database()
    generator = TestDataGenerator()

    await generator.generate_test_data(
        building_count=1000,  # Количество зданий
        organization_count=5000  # Количество организаций
    )


if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main())