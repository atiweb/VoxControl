import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:voxcontrol/providers/auth_provider.dart';
import 'package:voxcontrol/services/api_service.dart';
import 'package:voxcontrol/services/websocket_service.dart';

enum VoxConnectionState { disconnected, connecting, connected, error }

class ConnectionProvider extends ChangeNotifier {
  final WebSocketService _ws = WebSocketService();
  
  VoxConnectionState _state = VoxConnectionState.disconnected;
  String? _lastResponse;
  List<Map<String, String>> _history = [];
  Map<String, dynamic>? _serverConfig;
  String? _errorMessage;
  bool _isProcessing = false;

  AuthProvider? _auth;
  ApiService? get _api => _auth?.api;

  VoxConnectionState get state => _state;
  String? get lastResponse => _lastResponse;
  List<Map<String, String>> get history => List.unmodifiable(_history);
  Map<String, dynamic>? get serverConfig => _serverConfig;
  String? get errorMessage => _errorMessage;
  bool get isProcessing => _isProcessing;
  bool get isConnected => _state == VoxConnectionState.connected;

  void updateAuth(AuthProvider auth) {
    _auth = auth;
    if (auth.isAuthenticated && _state == ConnectionState.disconnected) {
      connect();
    }
  }

  /// Connect to the VoxControl server via WebSocket.
  void connect() {
    if (_auth?.serverUrl == null) return;

    _state = VoxConnectionState.connecting;
    notifyListeners();

    final httpUrl = _auth!.serverUrl!;
    final wsUrl = httpUrl
        .replaceFirst('https://', 'wss://')
        .replaceFirst('http://', 'ws://');

    _ws.onMessage = _handleMessage;
    _ws.onConnected = () {
      _state = VoxConnectionState.connected;
      notifyListeners();
    };
    _ws.onDisconnected = () {
      _state = VoxConnectionState.disconnected;
      notifyListeners();
    };
    _ws.onError = (error) {
      _state = VoxConnectionState.error;
      _errorMessage = error;
      notifyListeners();
    };

    _ws.connect(url: '$wsUrl/ws', token: _auth?.token);
  }

  void _handleMessage(Map<String, dynamic> message) {
    final type = message['type'] as String?;
    final data = message['data'];

    switch (type) {
      case 'config':
        _serverConfig = data is Map<String, dynamic> ? data : null;
        notifyListeners();
        break;
      case 'status':
        _state = VoxConnectionState.connected;
        notifyListeners();
        break;
      case 'response':
        _lastResponse = data?.toString();
        _isProcessing = false;
        if (_lastResponse != null) {
          _history.add({'type': 'response', 'text': _lastResponse!});
        }
        notifyListeners();
        break;
      case 'error':
        _errorMessage = data?.toString();
        _isProcessing = false;
        notifyListeners();
        break;
      case 'pong':
        break; // keepalive
    }
  }

  /// Send a text command (prefer REST for reliability).
  Future<void> sendCommand(String text) async {
    if (text.trim().isEmpty) return;

    _isProcessing = true;
    _history.add({'type': 'command', 'text': text});
    notifyListeners();

    try {
      // Use REST API for reliability
      if (_api != null && _api!.hasToken) {
        final result = await _api!.sendCommand(text);
        _lastResponse = result['response']?.toString();
      } else {
        // Fallback to WebSocket
        _ws.sendTextCommand(text);
        return; // response comes async
      }
    } catch (e) {
      _lastResponse = 'Error: $e';
    }

    _isProcessing = false;
    if (_lastResponse != null) {
      _history.add({'type': 'response', 'text': _lastResponse!});
    }
    notifyListeners();
  }

  /// Send audio data (base64 encoded).
  Future<void> sendAudio(String base64Audio) async {
    _isProcessing = true;
    notifyListeners();

    try {
      if (_api != null && _api!.hasToken) {
        final result = await _api!.sendAudio(base64Audio);
        _lastResponse = result['response']?.toString();
      } else {
        _ws.sendAudioData(base64Audio);
        return;
      }
    } catch (e) {
      _lastResponse = 'Error: $e';
    }

    _isProcessing = false;
    if (_lastResponse != null) {
      _history.add({'type': 'response', 'text': _lastResponse!});
    }
    notifyListeners();
  }

  void clearHistory() {
    _history = [];
    _lastResponse = null;
    notifyListeners();
  }

  void disconnect() {
    _ws.disconnect();
    _state = VoxConnectionState.disconnected;
    notifyListeners();
  }

  @override
  void dispose() {
    _ws.disconnect();
    super.dispose();
  }
}
