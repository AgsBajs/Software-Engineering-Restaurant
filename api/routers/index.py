from . import orders, order_details, guest_orders


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(guest_orders.router)