from __future__ import annotations

from flask import Flask, jsonify, request
from pydantic import ValidationError

from app.cache import cache
from app.db import db
from app.errors import ApiError
from app.routes import portfolio_bp, security_bp, trade_bp, user_bp


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    cache.init_app(app)

    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolios')
    app.register_blueprint(security_bp, url_prefix='/securities')
    app.register_blueprint(trade_bp, url_prefix='/trades')

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        allowed_origin = app.config.get('FRONTEND_ORIGIN', 'http://localhost:5173')
        if origin == allowed_origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
            response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        return response

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'}), 200

    @app.route('/health', methods=['OPTIONS'])
    def health_options():
        return ('', 204)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        db.session.rollback()
        return jsonify({'error': 'validation_error', 'detail': error.errors()}), 422

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        db.session.rollback()
        return jsonify({'error': error.error, 'detail': error.detail}), error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        db.session.rollback()
        return jsonify({'error': 'internal_server_error', 'detail': str(error)}), 500

    @app.teardown_request
    def teardown_request(exception):
        if exception is not None:
            db.session.rollback()

    return app
