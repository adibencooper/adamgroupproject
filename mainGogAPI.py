from fastapi import FastAPI, HTTPException, Query  
from fastapi.responses import JSONResponse         
from datetime import datetime, timedelta          
from dotenv import load_dotenv                   
from calendarCode import generateSlots, createEvent, getbusyTimes

load_dotenv()
app = FastAPI()


def parseDateTime(datestr: str, timestr: str = "00:00"):
    try:
        return datetime.strptime(f"{datestr} {timestr}", "%d/%m/%Y %H:%M")
    except:
        raise HTTPException(status_code=400, detail={"Status": "error", "Message": "Invalid format for date or time"})


def errorResponse(statuscode: int, message: str):
    return JSONResponse(statuscode=statuscode, content={"Status": "error", "Message": message})


@app.get("/check_availability")
def check_availability(date: str = Query(...), durationMins: int = Query(...)):
    try:
        startday = parseDateTime(date, "09:00")
        endday = parseDateTime(date, "17:00")

        slots = generateSlots(startday.isoformat() + "Z", endday.isoformat() + "Z", durationMins)

        formattedSlots = [
            datetime.fromisoformat(slot["start"].replace("Z", "")).strftime("%H:%M")
            for slot in slots
        ]

        return {"Availaible slots": formattedSlots}

    except HTTPException as e:
        raisast
    except Exception:
        return errorResponse(500, "Unexpected server error")


@app.post("/confirm_booking")
def confirm_booking(payload: dict):
    try:
        name = payload.get("Name")
        email = payload.get("Email")
        date = payload.get("Date")
        starttime = payload.get("Start time")
        duration = payload.get("DurationMins")

        if not all([name, email, date, starttime, duration]):
            return errorResponse(400, "Missing required fields")

        startdt = parseDateTime(date, starttime)
        enddt = startdt + timedelta(minutes=int(duration))

        startiso = startdt.isoformat() + "Z"
        endiso = enddt.isoformat() + "Z"

        busy = getbusyTimes(startiso, endiso)
        if busy:
            return errorResponse(409, "Selected time is no longer available")

        event = createEvent(startiso, endiso, f"Meeting with {name}", f"Booked by {name} ({email})")

        return{
            "Status": "confirmed",
            "Event_ID": event["id"],
            "Start": startdt.strftime("%d/%m/%Y %H:%M"),
            "End": enddt.strftime("%d/%m/%Y %H:%M")
        }
    except ValueError:
        return errorResponse(400, "Invalid duration format")
    except Exception:
        return errorResponse(502, "Google Calendar API error")