import os
from datetime import datetime
from typing import Optional

import requests
from dotenv import load_dotenv

from ssh_utils import SSHSession
from gpu_parser import parse_gpu_process_mapping, get_username_by_pid


class NotionClient:
    """Minimal Notion API client for upserting GPU information."""

    def __init__(self, token: str, database_id: str):
        self.database_id = database_id
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            }
        )

    # ------------------------------------------------------------------
    def _find_page(self, machine: str, gpu_index: int) -> Optional[str]:
        """Return page ID for ``machine`` and ``gpu_index`` if exists."""
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"
        payload = {
            "filter": {
                "and": [
                    {"property": "マシン名", "title": {"equals": machine}},
                    {"property": "GPU番号", "number": {"equals": gpu_index}},
                ]
            }
        }
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return results[0]["id"] if results else None

    # ------------------------------------------------------------------
    def upsert_gpu(self, machine: str, gpu_index: int, state: str, user: str,
                   timestamp: str, status: str) -> None:
        """Create or update a GPU entry in the Notion database."""
        page_id = self._find_page(machine, gpu_index)
        props = {
            "マシン名": {"title": [{"text": {"content": machine}}]},
            "GPU番号": {"number": gpu_index},
            "状態": {"select": {"name": state}},
            "使用ユーザー": {"rich_text": [{"text": {"content": user}}]},
            "最終更新時刻": {"rich_text": [{"text": {"content": timestamp}}]},
            "ステータス": {"select": {"name": status}},
        }
        if page_id:
            url = f"https://api.notion.com/v1/pages/{page_id}"
            payload = {"properties": props}
            resp = self.session.patch(url, json=payload)
        else:
            url = "https://api.notion.com/v1/pages"
            payload = {"parent": {"database_id": self.database_id}, "properties": props}
            resp = self.session.post(url, json=payload)
        resp.raise_for_status()


# ----------------------------------------------------------------------
def main():
    """Collect GPU info and upsert into Notion database."""
    load_dotenv()
    token = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")
    if not token or not database_id:
        raise RuntimeError("NOTION_TOKEN and NOTION_DATABASE_ID must be set")

    notion = NotionClient(token, database_id)
    machine_list = [
        "GPU1",
        "GPU2",
        "GPU3",
        "GPU4",
        "GPU5",
        "GPU6",
        "GPU7",
        "GPU200",
        "GPU201",
        "GPU202",
    ]

    for machine in machine_list:
        print(f"\n{'=' * 10} {machine} {'=' * 10}")
        try:
            with SSHSession(machine) as session:
                gpu_cmd = "nvidia-smi --query-gpu=index,uuid --format=csv,noheader"
                index_output = session.run(gpu_cmd)

                apps_cmd = (
                    "nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader"
                )
                apps_output = session.run(apps_cmd)

                mapping = parse_gpu_process_mapping(index_output, apps_output)
                for gpu_index, pid in mapping.items():
                    if pid is None:
                        state = "空き"
                        user = ""
                    else:
                        user = get_username_by_pid(machine, pid, session=session)
                        state = "使用中"
                        if user is None:
                            user = "ユーザー不明"
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    notion.upsert_gpu(machine, gpu_index, state, user, timestamp, "成功")
                    print(f"GPU{gpu_index}: {state} {user}")
        except Exception as e:
            print(f"[エラー] {machine} の取得に失敗しました: {e}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notion.upsert_gpu(machine, -1, "", "", timestamp, "失敗")


if __name__ == "__main__":
    main()
