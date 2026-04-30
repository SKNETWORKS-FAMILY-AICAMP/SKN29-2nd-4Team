# front/api/app_client.py

from typing import Dict, Any, List, Optional
import requests


class AppClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        res = requests.post(url, json=json)
        res.raise_for_status()
        return res.json()

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()


    def get_reservation_rank(
        self,
        depart: str,
        arrive: str,
    ) -> List[Dict[str, Any]]:
        res = self._post(
            "/api/reservation-rank",
            {
                "depart": depart,
                "arrive": arrive,
            },
        )

        # 스펙 변경 대응: 안전하게 접근
        return res.get("items", [])


    def check_my_reservation(
        self,
        reservation: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self._post(
            "/api/check-my-reservation",
            reservation,
        )


    def get_olearn_result(
        self,
        model_name: str,
    ) -> Dict[str, Any]:
        return self._get(
            f"/api/online-learning/{model_name}/result"
        )