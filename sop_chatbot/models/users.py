from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from .. import session
from ..models.companies import Company, CreateCompanyRequest
from ..models.departments import CreateDepartmentRequest, Department
from ..models.mixins import CLASS_MAPPING, BaseClass, BaseRequest
from ..services.auth import Auth


class UserRoles(str, Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'


class CreateUserRequest(BaseRequest):
    name: Annotated[str, Field(description='The name of the user')]
    password: Annotated[str, Field(description='The password of the user')]
    role: Annotated[UserRoles, Field(description='The role of the user')] = (
        UserRoles.USER
    )


class CreateAdminRequest(CreateUserRequest):
    email: Annotated[
        EmailStr,
        Field(
            description='The email of the user. Only the owner of the plan'
            + ' has their email registrationed'
        ),
    ]
    company_name: Annotated[str, Field(description='The name of the company')]
    company_description: Annotated[
        str, Field(description='The description of the company')
    ]


class CreateCommonUserRequest(CreateUserRequest):
    company: Annotated[str, Field(description='The company of the user')]
    departments: Annotated[
        list[str], Field(description='The department of the user')
    ] = []


class BaseUser(BaseClass, CreateUserRequest, ABC):
    company: Annotated[
        str, Field(description='The company of the user', min_length=12)
    ]

    @classmethod
    def table_name(cls):
        return 'users'

    @classmethod
    @abstractmethod
    async def gen_registration(
        cls, owner: str | None
    ) -> tuple[str, str]:  # pragma: no cover  # noqa: E501
        pass

    @classmethod
    @abstractmethod
    async def create(
        cls, create_request: CreateUserRequest, owner: str | None = None
    ):  # pragma: no cover
        created_at = datetime.now()
        updated_at = datetime.now()
        registration, updated_owner = await cls.gen_registration(owner)
        create_request.password = Auth.encrypt_password(
            create_request.password
        )
        id = (
            await session.db[cls.table_name()].insert_one(
                {
                    **create_request.mongo(),
                    'owner': updated_owner,
                    'registration': registration,
                    'created_at': created_at,
                    'updated_at': updated_at,
                }
            )
        ).inserted_id
        self = cls(
            id=str(id),
            registration=registration,
            owner=updated_owner,
            created_at=created_at,
            updated_at=updated_at,
            **create_request.model_dump(),
        )
        return self

    @classmethod
    async def get(cls, registration: str):
        obj = await session.db[cls.table_name()].find_one(
            {'registration': registration}
        )
        if obj:
            return cls(
                id=str(obj['_id']),
                **obj,
            )
        return None

    def json(self) -> dict:
        dump = super().json()
        dump.pop('password', None)
        return dump

    def mongo(self) -> dict:
        dump = super().mongo()
        dump.pop('password', None)
        return dump

    def verify_password(self, password: str) -> bool:
        return self.password == Auth.encrypt_password(password)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRoles.ADMIN

    @property
    def is_manager(self) -> bool:
        return self.role == UserRoles.MANAGER or self.is_admin


class UserResponse(BaseModel):
    registration: Annotated[
        str, Field(description='The registration of the user')
    ]
    owner: Annotated[str, Field(description='The owner of the user')]
    name: Annotated[str, Field(description='The name of the user')]
    departments: Annotated[
        list[str], Field(description='The department list of the user')
    ]
    company: Annotated[str, Field(description='The company of the user')]
    role: Annotated[UserRoles, Field(description='The role of the user')] = (
        UserRoles.USER
    )


class AdminResponse(UserResponse):
    email: Annotated[
        EmailStr,
        Field(
            description='The email of the user. Only the owner of the'
            + ' plan has their email registrationed'
        ),
    ]


class User(BaseUser, CreateCommonUserRequest):
    @classmethod
    async def gen_registration(cls, owner: str) -> tuple[str, str]:
        pipeline = [
            {'$match': {'owner': owner}},
            {
                '$project': {
                    'registration': {
                        '$toInt': {
                            '$substr': [
                                '$registration',
                                {
                                    '$add': [
                                        {
                                            '$indexOfBytes': [
                                                '$registration',
                                                '.',
                                            ]
                                        },
                                        1,
                                    ]
                                },
                                {
                                    '$subtract': [
                                        {'$strLenCP': '$registration'},
                                        {
                                            '$add': [
                                                {
                                                    '$indexOfBytes': [
                                                        '$registration',
                                                        '.',
                                                    ]
                                                },
                                                1,
                                            ]
                                        },
                                    ]
                                },
                            ]
                        }
                    }
                }
            },
            {'$sort': {'registration': -1}},
            {'$limit': 1},
        ]
        result = (
            await session.db[cls.table_name()]
            .aggregate(pipeline)
            .to_list(length=1)
        )
        highest_registration = result[0]['registration']
        return '.'.join(owner.split('.')[0:2]) + '.' + str(
            highest_registration
        ).zfill(3), owner

    @classmethod
    async def create(cls, create_request: CreateCommonUserRequest, owner: str):
        created_at = datetime.now()
        updated_at = datetime.now()
        registration, updated_owner = await cls.gen_registration(owner)
        create_request.password = Auth.encrypt_password(
            create_request.password
        )
        id = (
            await session.db[cls.table_name()].insert_one(
                {
                    **create_request.mongo(),
                    'owner': updated_owner,
                    'registration': registration,
                    'created_at': created_at,
                    'updated_at': updated_at,
                }
            )
        ).inserted_id
        self = cls(
            id=str(id),
            registration=registration,
            owner=updated_owner,
            created_at=created_at,
            updated_at=updated_at,
            **create_request.model_dump(),
        )
        return self


class Admin(BaseUser, CreateAdminRequest):
    role: Annotated[UserRoles, Field(description='The role of the user')] = (
        UserRoles.ADMIN
    )
    departments: Annotated[
        list[str], Field(description='The department of the user')
    ]

    @classmethod
    async def gen_registration(cls, owner: None = None) -> tuple[str, str]:
        registration = CLASS_MAPPING['User'] + '.'
        all_users = await session.db[cls.table_name()].count_documents({})
        registration += str(all_users + 1).zfill(4)
        registration += '.000'
        return registration, registration

    @classmethod
    async def create(cls, create_request: CreateAdminRequest, owner: str):
        created_at = datetime.now()
        updated_at = datetime.now()
        registration, updated_owner = await cls.gen_registration(owner)
        company = await Company.create(
            CreateCompanyRequest(
                name=create_request.company_name,
                description=create_request.company_description,
            ),
            owner=registration,
        )
        department = await Department.create(
            CreateDepartmentRequest(
                name='administration',
                description=' '.join(
                    (
                        'This department is only accessible',
                        'by the administration',
                    )
                ),
            ),
            owner=company.owner,
            company=company.registration,
        )
        create_request.password = Auth.encrypt_password(
            create_request.password
        )
        id = (
            await session.db[cls.table_name()].insert_one(
                {
                    **create_request.mongo(),
                    'owner': updated_owner,
                    'registration': registration,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'company': company.registration,
                    'departments': [department.registration],
                }
            )
        ).inserted_id
        self = cls(
            id=str(id),
            registration=registration,
            owner=updated_owner,
            created_at=created_at,
            updated_at=updated_at,
            company=company.registration,
            departments=[department.registration],
            **create_request.model_dump(),
        )
        return self


class UpdateUserRequest(BaseRequest):
    name: Annotated[str | None, Field(description='The name of the user')] = (
        None
    )
    departments: Annotated[
        str | None, Field(description='The department of the user')
    ] = None
    company: Annotated[
        str | None, Field(description='The company of the user')
    ] = None
    role: Annotated[
        UserRoles | None, Field(description='The role of the user')
    ] = None
