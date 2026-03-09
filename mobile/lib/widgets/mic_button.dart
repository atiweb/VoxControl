import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:record/record.dart';
import 'package:voxcontrol/providers/connection_provider.dart';
import 'package:voxcontrol/theme/app_theme.dart';

class MicButton extends StatefulWidget {
  const MicButton({super.key});

  @override
  State<MicButton> createState() => _MicButtonState();
}

class _MicButtonState extends State<MicButton>
    with SingleTickerProviderStateMixin {
  final AudioRecorder _recorder = AudioRecorder();
  bool _isRecording = false;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );
    _pulseAnimation = Tween(begin: 1.0, end: 1.15).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _recorder.dispose();
    super.dispose();
  }

  Future<void> _startRecording() async {
    if (await _recorder.hasPermission()) {
      await _recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
          bitRate: 256000,
        ),
        path: '', // Use stream
      );
      setState(() => _isRecording = true);
      _pulseController.repeat(reverse: true);
    }
  }

  Future<void> _stopRecording() async {
    final path = await _recorder.stop();
    setState(() => _isRecording = false);
    _pulseController.stop();
    _pulseController.reset();

    if (path == null) return;

    // Read file and send as base64
    // In a real implementation, you'd stream audio or use the path
    // For now, send via REST API as text indication
    if (!mounted) return;
    final conn = context.read<ConnectionProvider>();
    conn.sendCommand('[voice recording sent]');
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _pulseAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _isRecording ? _pulseAnimation.value : 1.0,
          child: Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: _isRecording
                    ? [AppTheme.error, AppTheme.error.withValues(alpha: 0.8)]
                    : [AppTheme.primary, AppTheme.accent],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              boxShadow: [
                BoxShadow(
                  color: (_isRecording ? AppTheme.error : AppTheme.primary)
                      .withValues(alpha: 0.3),
                  blurRadius: 16,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                customBorder: const CircleBorder(),
                onTapDown: (_) => _startRecording(),
                onTapUp: (_) => _stopRecording(),
                onTapCancel: () => _stopRecording(),
                child: Icon(
                  _isRecording ? Icons.mic : Icons.mic_none,
                  color: Colors.white,
                  size: 28,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

/// Workaround: AnimatedBuilder that works like AnimatedWidget.
class AnimatedBuilder extends AnimatedWidget {
  final Widget Function(BuildContext context, Widget? child) builder;
  final Widget? child;

  const AnimatedBuilder({
    super.key,
    required Animation<double> animation,
    required this.builder,
    this.child,
  }) : super(listenable: animation);

  @override
  Widget build(BuildContext context) => builder(context, child);
}
