from typing import Dict, Any, List, Optional
import requests

from front.api.schema import Reservation, ReservationRankRequest


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
        request: ReservationRankRequest
    ) -> List[Dict[str, Any]]:
        res = self._post(
            "/api/reservation-rank",
            request.model_dump(mode="json"),
        )

        # 스펙 변경 대응: 안전하게 접근
        return res.get("items", [])


    def check_my_reservation(
        self,
        reservation: Reservation,
    ) -> Dict[str, Any]:
        print("DEBUG reservation: ", reservation)
        return self._post(
            "/api/check-my-reservation",
            reservation.model_dump(mode="json"),
        )


    def get_olearn_result(
        self,
        model_name: str,
    ) -> Dict[str, Any]:
        return self._get(
            f"/api/online-learning/{model_name}/result"
        )
    
    def get_airports(self):
        return self._get("/lookup/airports")

    def get_airlines(self):
        return self._get("/lookup/airlines")