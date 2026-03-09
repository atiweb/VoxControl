/// WebSocket service for real-time communication with VoxControl backend.

import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

typedef MessageCallback = void Function(Map<String, dynamic> message);

class WebSocketService {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _pingTimer;
  Timer? _reconnectTimer;

  String _wsUrl = '';
  String? _token;
  bool _shouldReconnect = true;
  int _reconnectAttempts = 0;
  static const _maxReconnectAttempts = 10;
  static const _reconnectBaseDelay = Duration(seconds: 2);

  MessageCallback? onMessage;
  VoidCallback? onConnected;
  VoidCallback? onDisconnected;
  void Function(String error)? onError;

  bool get isConnected => _channel != null;

  void connect({required String url, String? token}) {
    _wsUrl = url;
    _token = token;
    _shouldReconnect = true;
    _reconnectAttempts = 0;
    _doConnect();
  }

  void _doConnect() {
    disconnect(permanent: false);

    try {
      var uri = Uri.parse(_wsUrl);
      if (_token != null) {
        uri = uri.replace(queryParameters: {'token': _token!});
      }

      _channel = WebSocketChannel.connect(uri);

      _subscription = _channel!.stream.listen(
        (data) {
          _reconnectAttempts = 0;
          try {
            final message = jsonDecode(data as String) as Map<String, dynamic>;
            onMessage?.call(message);
          } catch (_) {}
        },
        onError: (error) {
          onError?.call(error.toString());
          _scheduleReconnect();
        },
        onDone: () {
          onDisconnected?.call();
          _scheduleReconnect();
        },
      );

      // Start ping timer
      _pingTimer?.cancel();
      _pingTimer = Timer.periodic(const Duration(seconds: 15), (_) {
        sendMessage({'type': 'ping'});
      });

      onConnected?.call();
    } catch (e) {
      onError?.call(e.toString());
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    _channel = null;
    _pingTimer?.cancel();

    if (!_shouldReconnect ||
        _reconnectAttempts >= _maxReconnectAttempts) return;

    final delay = _reconnectBaseDelay * (1 << _reconnectAttempts.clamp(0, 5));
    _reconnectAttempts++;

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(delay, _doConnect);
  }

  void sendMessage(Map<String, dynamic> message) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode(message));
    }
  }

  void sendTextCommand(String text) {
    sendMessage({'type': 'text', 'data': text});
  }

  void sendAudioData(String base64Audio) {
    sendMessage({'type': 'audio_b64', 'data': base64Audio});
  }

  void disconnect({bool permanent = true}) {
    if (permanent) _shouldReconnect = false;
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    _subscription?.cancel();
    _channel?.sink.close();
    _channel = null;
  }
}

typedef VoidCallback = void Function();
