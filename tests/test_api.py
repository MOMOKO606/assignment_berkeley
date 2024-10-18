import pytest
from uuid import UUID
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from fastapi import HTTPException


from assignment_berkeley.db.models import DBCustomer, DBOrder, DBProduct, Base
from assignment_berkeley.helpers.db_helpers import with_session, validate_and_get_item


class TestWithSession:
    def test_successful_read_operation(self):
        # 创建一个模拟的类和方法
        class DummyClass:
            @with_session
            def dummy_read(self, session=None):
                return "success"

        # 测试读操作
        dummy = DummyClass()
        result = dummy.dummy_read()
        assert result == "success"

    def test_successful_write_operation(self):
        # 模拟写操作（create/update/delete）
        class DummyClass:
            @with_session
            def create(self, session=None):
                return "created"

        dummy = DummyClass()
        result = dummy.create()
        assert result == "created"

    def test_exception_handling(self):
        # 测试异常处理
        class DummyClass:
            @with_session
            def create(self, session=None):
                raise ValueError("Test error")

        dummy = DummyClass()
        with pytest.raises(HTTPException) as exc_info:
            dummy.create()
        assert exc_info.value.status_code == 400
        assert "Test error" in str(exc_info.value.detail)

    @patch("assignment_berkeley.db.engine.DBSession")
    def test_session_management(self, mock_db_session):
        # 创建模拟的session对象
        mock_session = Mock()
        mock_db_session.return_value = mock_session

        class DummyClass:
            @with_session
            def create(self, session=None):
                return "success"

        dummy = DummyClass()
        dummy.create()

        # 验证session的正确使用
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("assignment_berkeley.db.engine.DBSession")
    def test_session_rollback_on_error(self, mock_db_session):
        # 测试出错时的回滚操作
        mock_session = Mock()
        mock_db_session.return_value = mock_session

        class DummyClass:
            @with_session
            def create(self, session=None):
                raise ValueError("Test error")

        dummy = DummyClass()
        with pytest.raises(HTTPException):
            dummy.create()

        # 验证回滚被调用
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


class TestValidateAndGetItem:
    def setup_method(self):
        self.mock_session = Mock(spec=Session)
        self.valid_uuid = "123e4567-e89b-12d3-a456-426614174000"

    def test_valid_uuid_customer(self):
        # 测试有效的UUID
        mock_customer = Mock(spec=DBCustomer)
        self.mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_customer
        )

        result = validate_and_get_item(self.mock_session, self.valid_uuid, DBCustomer)
        assert result == mock_customer

    def test_invalid_uuid_format(self):
        # 测试无效的UUID格式
        with pytest.raises(HTTPException) as exc_info:
            validate_and_get_item(self.mock_session, "invalid-uuid", DBCustomer)
        assert exc_info.value.status_code == 400
        assert "Invalid UUID format" in str(exc_info.value.detail)

    def test_not_found_item(self):
        # 测试找不到对应记录的情况
        self.mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_and_get_item(self.mock_session, self.valid_uuid, DBCustomer)
        assert exc_info.value.status_code == 404
        assert "Customer not found" in str(exc_info.value.detail)

    def test_with_integer_id(self):
        # 测试使用整数ID
        mock_product = Mock(spec=DBProduct)
        self.mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_product
        )

        result = validate_and_get_item(self.mock_session, 123, DBProduct)
        assert result == mock_product

    def test_unknown_db_class(self):
        # 测试未映射的数据库类
        class UnknownModel(Base):
            __tablename__ = "unknown"

        self.mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_and_get_item(self.mock_session, self.valid_uuid, UnknownModel)
        assert "Unknown not found" in str(exc_info.value.detail)


# 运行测试的辅助函数
def run_tests():
    pytest.main([__file__])


if __name__ == "__main__":
    run_tests()
