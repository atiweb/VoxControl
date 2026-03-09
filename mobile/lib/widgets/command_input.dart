import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:voxcontrol/providers/connection_provider.dart';

class CommandInput extends StatefulWidget {
  const CommandInput({super.key});

  @override
  State<CommandInput> createState() => _CommandInputState();
}

class _CommandInputState extends State<CommandInput> {
  final _controller = TextEditingController();

  void _send() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    context.read<ConnectionProvider>().sendCommand(text);
    _controller.clear();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      decoration: BoxDecoration(
        color: Theme.of(context).appBarTheme.backgroundColor,
        border: Border(
          top: BorderSide(
            color: Colors.white.withValues(alpha: 0.06),
          ),
        ),
      ),
      // Leave space for floating mic button
      child: Padding(
        padding: const EdgeInsets.only(bottom: 48),
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _send(),
                decoration: InputDecoration(
                  hintText: 'Type a command...',
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide(
                      color: Colors.white.withValues(alpha: 0.1),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              onPressed: _send,
              icon: Icon(
                Icons.send,
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
