import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:voxcontrol/services/api_service.dart';

enum AuthState { initial, loading, authenticated, unauthenticated, error }

class AuthProvider extends ChangeNotifier {
  final _storage = const FlutterSecureStorage();
  
  AuthState _state = AuthState.initial;
  String? _token;
  String? _username;
  String? _serverUrl;
  String? _errorMessage;
  bool _authRequired = true;
  bool _hasUsers = true;

  AuthState get state => _state;
  String? get token => _token;
  String? get username => _username;
  String? get serverUrl => _serverUrl;
  String? get errorMessage => _errorMessage;
  bool get authRequired => _authRequired;
  bool get hasUsers => _hasUsers;
  bool get isAuthenticated => _state == AuthState.authenticated;

  ApiService? _api;
  ApiService? get api => _api;

  /// Initialize from saved credentials.
  Future<void> init() async {
    _serverUrl = await _storage.read(key: 'server_url');
    _token = await _storage.read(key: 'token');
    _username = await _storage.read(key: 'username');

    if (_serverUrl != null && _serverUrl!.isNotEmpty) {
      _api = ApiService(baseUrl: _serverUrl!, token: _token);
    }

    if (_serverUrl != null && _token != null) {
      // Validate token
      try {
        _state = AuthState.loading;
        notifyListeners();
        await _api!.getStatus();
        _state = AuthState.authenticated;
      } catch (_) {
        _token = null;
        _state = AuthState.unauthenticated;
      }
    } else {
      _state = AuthState.unauthenticated;
    }
    notifyListeners();
  }

  /// Set server URL and check auth status.
  Future<void> setServer(String url) async {
    _serverUrl = url;
    _api = ApiService(baseUrl: url);
    await _storage.write(key: 'server_url', value: url);

    try {
      _state = AuthState.loading;
      notifyListeners();
      final status = await _api!.getAuthStatus();
      _authRequired = status['auth_required'] == true;
      _hasUsers = status['has_users'] == true;

      if (!_authRequired) {
        // No auth needed — auto connect
        _state = AuthState.authenticated;
        _username = 'local';
        await _storage.write(key: 'username', value: 'local');
      } else {
        _state = AuthState.unauthenticated;
      }
    } catch (e) {
      _state = AuthState.error;
      _errorMessage = 'Cannot reach server: $url';
    }
    notifyListeners();
  }

  /// Register first user (only works if no users exist).
  Future<bool> register(String username, String password) async {
    if (_api == null) return false;
    try {
      _state = AuthState.loading;
      notifyListeners();
      final result = await _api!.register(username, password);
      _token = result['token'] as String;
      _username = result['username'] as String;
      _api!.setToken(_token);
      await _storage.write(key: 'token', value: _token);
      await _storage.write(key: 'username', value: _username);
      _state = AuthState.authenticated;
      notifyListeners();
      return true;
    } on ApiException catch (e) {
      _state = AuthState.unauthenticated;
      _errorMessage = e.message;
      notifyListeners();
      return false;
    }
  }

  /// Login with existing credentials.
  Future<bool> login(String username, String password) async {
    if (_api == null) return false;
    try {
      _state = AuthState.loading;
      notifyListeners();
      final result = await _api!.login(username, password);
      _token = result['token'] as String;
      _username = result['username'] as String;
      _api!.setToken(_token);
      await _storage.write(key: 'token', value: _token);
      await _storage.write(key: 'username', value: _username);
      _state = AuthState.authenticated;
      notifyListeners();
      return true;
    } on ApiException catch (e) {
      _state = AuthState.unauthenticated;
      _errorMessage = e.message;
      notifyListeners();
      return false;
    }
  }

  /// Logout and clear credentials.
  Future<void> logout() async {
    _token = null;
    _username = null;
    _state = AuthState.unauthenticated;
    await _storage.delete(key: 'token');
    await _storage.delete(key: 'username');
    notifyListeners();
  }
}
