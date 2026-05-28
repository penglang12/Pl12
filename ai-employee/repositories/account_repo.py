"""账号仓库 - Account 模型的所有 DB 操作。"""

from typing import List, Optional

from core.db import db
from core.errors import NotFoundError
from core.models import Account


class AccountRepository:
    """社交媒体账号数据访问层。"""

    def create(
        self,
        platform: str,
        account_id: str,
        nickname: Optional[str] = None,
        cookies_json: Optional[str] = None,
    ) -> Account:
        session = db.session
        account = Account(
            platform=platform,
            account_id=account_id,
            nickname=nickname,
            cookies_json=cookies_json,
            status="active",
        )
        session.add(account)
        session.commit()
        return account

    def get(self, account_id: int) -> Account:
        session = db.session
        account = session.query(Account).get(account_id)
        if not account:
            raise NotFoundError(f"账号 {account_id}")
        return account

    def find_by_platform(self, platform: str) -> List[Account]:
        session = db.session
        return (
            session.query(Account)
            .filter(Account.platform == platform, Account.status == "active")
            .all()
        )

    def update_cookies(self, account_id: int, cookies_json: str) -> Account:
        account = self.get(account_id)
        account.cookies_json = cookies_json
        db.session.commit()
        return account

    def delete(self, account_id: int) -> None:
        account = self.get(account_id)
        account.status = "deleted"
        db.session.commit()


# 全局单例
account_repo = AccountRepository()
