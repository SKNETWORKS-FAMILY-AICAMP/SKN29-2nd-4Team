# convertor

# make_rows

# make_one

def make_input(start_airport, end_airport, start_datetime, end_datetime, airline):
    """
    입력:
    출발 도착 공항코드
    출발 도착 시각
    항공사
    """

def make_all_inputs(start_airport, end_airport):
    """
    현재시간 + 7일동안의 시간
    항공사는 최빈값
    """


"""
    chunk["CRSDepHour"] = (chunk["CRSDepMinutes"] // 60).astype(int)
    chunk["CRSArrHour"] = (chunk["CRSArrMinutes"] // 60).astype(int)

    chunk["CRSDep_sin"] = np.sin(2 * np.pi * chunk["CRSDepMinutes"] / 1440)
    chunk["CRSDep_cos"] = np.cos(2 * np.pi * chunk["CRSDepMinutes"] / 1440)
    chunk["CRSArr_sin"] = np.sin(2 * np.pi * chunk["CRSArrMinutes"] / 1440)
    chunk["CRSArr_cos"] = np.cos(2 * np.pi * chunk["CRSArrMinutes"] / 1440)
"""