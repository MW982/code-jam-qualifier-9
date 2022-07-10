import typing
from dataclasses import dataclass
from random import choice


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RequestType:
    ON_DUTY = "staff.onduty"
    OFF_DUTY = "staff.offduty"
    ORDER = "order"

class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}
        self.specialities = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        type_ = request.scope.get("type")
        id_ = request.scope.get("id")
        specialities = request.scope.get("speciality")
        if type_ == RequestType.ON_DUTY:
            self.staff[id_] = request
            for s in specialities:
                if s not in self.specialities:
                    self.specialities[s] = []
                self.specialities[s].append(id_)
        elif type_ == RequestType.OFF_DUTY:
            self.staff.pop(id_)
        elif type_ == RequestType.ORDER:
            try:
                staff_id = self.specialities.get(specialities)[0]
                staff_member = self.staff.get(staff_id)
            except IndexError:
                # If there's no staff available with
                # required speciality pick random staff
                staff_member = choice(list(self.staff.values()))

            full_order = await request.receive()
            await staff_member.send(full_order)

            result = await staff_member.receive()
            await request.send(result)
