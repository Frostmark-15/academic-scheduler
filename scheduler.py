
from itertools import product

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday"
]

START_HOUR = 8
END_HOUR = 18


def overlaps(start1, end1, start2, end2):

    return start1 < end2 and start2 < end1


def generate_schedule(subjects, rooms):

    if not subjects or not rooms:
        return None

    meetings = []

    # Expand subjects into individual weekly meetings
    for subject in subjects:

        for number in range(1, subject["meetings"] + 1):

            meetings.append({
                "subject": subject,
                "meeting_no": number,
                "duration": subject["duration"]
            })

    # Schedule longer meetings first
    meetings.sort(
        key=lambda item: -item["duration"]
    )

    assignments = []

    instructor_busy = {}
    section_busy = {}
    room_busy = {}

    def available(busy, key, day, start, end):

        for existing_day, existing_start, existing_end in busy.get(key, []):

            if existing_day == day:

                if overlaps(
                    start,
                    end,
                    existing_start,
                    existing_end
                ):
                    return False

        return True


    def find_candidates(meeting):

        subject = meeting["subject"]

        preferred = [
            day for day in subject["preferred_days"]
            if day in DAYS
        ]

        days = preferred + [
            day for day in DAYS
            if day not in preferred
        ]

        starts = range(
            START_HOUR,
            END_HOUR - meeting["duration"] + 1
        )

        for day, start, room in product(
            days,
            starts,
            rooms
        ):

            end = start + meeting["duration"]

            yield day, start, end, room["room_name"]


    def solve(index):

        if index == len(meetings):
            return True

        meeting = meetings[index]

        subject = meeting["subject"]

        instructor = subject["instructor"].strip().lower()

        section = subject["section"].strip().lower()

        for day, start, end, room in find_candidates(meeting):

            if not available(
                instructor_busy,
                instructor,
                day,
                start,
                end
            ):
                continue

            if not available(
                section_busy,
                section,
                day,
                start,
                end
            ):
                continue

            if not available(
                room_busy,
                room,
                day,
                start,
                end
            ):
                continue

            # Assign resources

            instructor_busy.setdefault(
                instructor, []
            ).append((day, start, end))

            section_busy.setdefault(
                section, []
            ).append((day, start, end))

            room_busy.setdefault(
                room, []
            ).append((day, start, end))

            assignments.append({
                "subject_id": subject["id"],
                "subject_code": subject["subject_code"],
                "subject_name": subject["subject_name"],
                "instructor": subject["instructor"],
                "section": subject["section"],
                "meeting_no": meeting["meeting_no"],
                "day": day,
                "start_hour": start,
                "end_hour": end,
                "room": room
            })

            if solve(index + 1):
                return True

            # Backtracking

            assignments.pop()

            instructor_busy[instructor].pop()

            section_busy[section].pop()

            room_busy[room].pop()

        return False


    if solve(0):
        return assignments

    return None
