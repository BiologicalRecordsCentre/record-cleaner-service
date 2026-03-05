from fastapi.testclient import TestClient

from sqlmodel import Session, select

from app.sqlmodels import User, Usage


class TestUsage:
    def test_all_usage_for_year(self, client: TestClient):

        # Get database connection from client.
        engine = client.app.context['engine']
        with Session(engine) as db:
            user = User(name='Test', email='test@test.com', hash='abc')
            db.add(user)
            db.commit()

            # Create usage stats.
            usage1 = Usage(
                user_name=user.name,
                year=2022,
                month=1,
                verification_requests=1,
                validation_requests=2,
                verification_records=3,
                validation_records=4
            )
            usage2 = Usage(
                user_name=user.name,
                year=2022,
                month=2,
                verification_requests=5,
                validation_requests=6,
                verification_records=7,
                validation_records=8
            )
            db.add(usage1)
            db.add(usage2)
            db.commit()

        response = client.get("/usage/2022")
        assert response.status_code == 200
        usages = response.json()
        assert len(usages) == 1
        usage = usages[0]
        assert usage['user_name'] == 'Test'
        assert usage['verification_requests'] == 6
        assert usage['validation_requests'] == 8
        assert usage['verification_records'] == 10
        assert usage['validation_records'] == 12

    def test_all_usage_for_year_month(self, client: TestClient):

        # Get database connection from client.
        engine = client.app.context['engine']
        with Session(engine) as db:
            user = User(name='Test', email='test@test.com', hash='abc')
            db.add(user)
            db.commit()

            # Create usage stats.
            usage1 = Usage(
                user_name=user.name,
                year=2022,
                month=1,
                verification_requests=1,
                validation_requests=2,
                verification_records=3,
                validation_records=4
            )
            db.add(usage1)
            db.commit()

        response = client.get("/usage/2022/1")
        assert response.status_code == 200
        usages = response.json()
        assert len(usages) == 1
        usage = usages[0]
        assert usage['user_name'] == 'Test'
        assert usage['verification_requests'] == 1
        assert usage['validation_requests'] == 2
        assert usage['verification_records'] == 3
        assert usage['validation_records'] == 4

    def test_usage_by_month(self, client: TestClient):

        # Get database connection from client.
        engine = client.app.context['engine']
        with Session(engine) as db:
            user = User(name='Test', email='test@test.com', hash='abc')
            db.add(user)
            db.commit()

            # Create usage stats.
            usage1 = Usage(
                user_name=user.name,
                year=2022,
                month=1,
                verification_requests=1,
                validation_requests=2,
                verification_records=3,
                validation_records=4
            )
            usage2 = Usage(
                user_name=user.name,
                year=2022,
                month=2,
                verification_requests=5,
                validation_requests=6,
                verification_records=7,
                validation_records=8
            )
            db.add(usage1)
            db.add(usage2)
            db.commit()

        response = client.get("/usage/user/Test/2022")
        assert response.status_code == 200
        usages = response.json()
        assert len(usages) == 2
        usage = usages[0]
        assert usage['month'] == 1
        assert usage['verification_requests'] == 1
        assert usage['validation_requests'] == 2
        assert usage['verification_records'] == 3
        assert usage['validation_records'] == 4
        usage = usages[1]
        assert usage['month'] == 2
        assert usage['verification_requests'] == 5
        assert usage['validation_requests'] == 6
        assert usage['verification_records'] == 7
        assert usage['validation_records'] == 8

    def test_usage_by_year(self, client: TestClient):

        # Get database connection from client.
        engine = client.app.context['engine']
        with Session(engine) as db:
            user = User(name='Test', email='test@test.com', hash='abc')
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create usage stats.
            usage1 = Usage(
                user_name=user.name,
                year=2022,
                month=1,
                verification_requests=1,
                validation_requests=2,
                verification_records=3,
                validation_records=4
            )
            usage2 = Usage(
                user_name=user.name,
                year=2022,
                month=2,
                verification_requests=5,
                validation_requests=6,
                verification_records=7,
                validation_records=8
            )
            usage3 = Usage(
                user_name=user.name,
                year=2023,
                month=1,
                verification_requests=8,
                validation_requests=7,
                verification_records=6,
                validation_records=5
            )
            usage4 = Usage(
                user_name=user.name,
                year=2023,
                month=2,
                verification_requests=4,
                validation_requests=3,
                verification_records=2,
                validation_records=1
            )
            db.add(usage1)
            db.add(usage2)
            db.add(usage3)
            db.add(usage4)
            db.commit()

        response = client.get("/usage/user/Test")
        assert response.status_code == 200
        usages = response.json()
        assert len(usages) == 2
        usage = usages[0]
        assert usage['year'] == 2022
        assert usage['verification_requests'] == 6
        assert usage['validation_requests'] == 8
        assert usage['verification_records'] == 10
        assert usage['validation_records'] == 12
        usage = usages[1]
        assert usage['year'] == 2023
        assert usage['verification_requests'] == 12
        assert usage['validation_requests'] == 10
        assert usage['verification_records'] == 8
        assert usage['validation_records'] == 6
