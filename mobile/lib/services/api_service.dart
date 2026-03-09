/// API service for communicating with the VoxControl backend.

import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  String _baseUrl;
  String? _token;

  ApiService({required String baseUrl, String? token})
      : _baseUrl = baseUrl.replaceAll(RegExp(r'/+$'), ''),
        _token = token;

  String get baseUrl => _baseUrl;
  bool get hasToken => _token != null && _token!.isNotEmpty;

  void updateBaseUrl(String url) {
    _baseUrl = url.replaceAll(RegExp(r'/+$'), '');
  }

  void setToken(String? token) {
    _token = token;
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  // ---- Auth ----

  Future<Map<String, dynamic>> getAuthStatus() async {
    final resp = await http.get(
      Uri.parse('$_baseUrl/api/auth/status'),
      headers: _headers,
    );
    return _parseResponse(resp);
  }

  Future<Map<String, dynamic>> register(
      String username, String password) async {
    final resp = await http.post(
      Uri.parse('$_baseUrl/api/auth/register'),
      headers: _headers,
      body: jsonEncode({'username': username, 'password': password}),
    );
    return _parseResponse(resp);
  }

  Future<Map<String, dynamic>> login(String username, String password) async {
    final resp = await http.post(
      Uri.parse('$_baseUrl/api/auth/login'),
      headers: _headers,
      body: jsonEncode({'username': username, 'password': password}),
    );
    return _parseResponse(resp);
  }

  // ---- Commands ----

  Future<Map<String, dynamic>> sendCommand(String text) async {
    final resp = await http.post(
      Uri.parse('$_baseUrl/api/command'),
      headers: _headers,
      body: jsonEncode({'text': text}),
    );
    return _parseResponse(resp);
  }

  Future<Map<String, dynamic>> sendAudio(String audioBase64) async {
    final resp = await http.post(
      Uri.parse('$_baseUrl/api/audio'),
      headers: _headers,
      body: jsonEncode({'audio_b64': audioBase64}),
    );
    return _parseResponse(resp);
  }

  // ---- Status ----

  Future<Map<String, dynamic>> getStatus() async {
    final resp = await http.get(
      Uri.parse('$_baseUrl/api/status'),
      headers: _headers,
    );
    return _parseResponse(resp);
  }

  Future<List<String>> getActions() async {
    final resp = await http.get(
      Uri.parse('$_baseUrl/api/actions'),
      headers: _headers,
    );
    final data = _parseResponse(resp);
    return List<String>.from(data['actions'] ?? []);
  }

  // ---- Helpers ----

  Map<String, dynamic> _parseResponse(http.Response resp) {
    final body = jsonDecode(resp.body) as Map<String, dynamic>;
    if (resp.statusCode >= 400) {
      throw ApiException(
        statusCode: resp.statusCode,
        message: body['detail']?.toString() ?? 'Request failed',
      );
    }
    return body;
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}
