from . import orders, order_details, guest_orders, menu_items, review, promotions


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(guest_orders.router)
    app.include_router(menu_items.router)
    app.include_router(review.router)
    app.include_router(promotions.router)