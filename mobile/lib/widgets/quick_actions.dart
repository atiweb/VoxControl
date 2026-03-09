import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:voxcontrol/providers/connection_provider.dart';

class QuickActions extends StatelessWidget {
  const QuickActions({super.key});

  static const _actions = [
    _QuickAction(Icons.language, 'Chrome', 'open chrome'),
    _QuickAction(Icons.chat, 'WhatsApp', 'open whatsapp'),
    _QuickAction(Icons.screenshot_monitor, 'Screenshot', 'take screenshot'),
    _QuickAction(Icons.volume_up, 'Vol +', 'volume up'),
    _QuickAction(Icons.volume_down, 'Vol -', 'volume down'),
    _QuickAction(Icons.minimize, 'Minimize', 'minimize'),
    _QuickAction(Icons.lock, 'Lock', 'lock screen'),
    _QuickAction(Icons.play_arrow, 'Play', 'play pause'),
  ];

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 90,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        itemCount: _actions.length,
        separatorBuilder: (_, __) => const SizedBox(width: 4),
        itemBuilder: (context, index) {
          final action = _actions[index];
          return _QuickActionChip(action: action);
        },
      ),
    );
  }
}

class _QuickAction {
  final IconData icon;
  final String label;
  final String command;

  const _QuickAction(this.icon, this.label, this.command);
}

class _QuickActionChip extends StatelessWidget {
  final _QuickAction action;

  const _QuickActionChip({required this.action});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        context.read<ConnectionProvider>().sendCommand(action.command);
      },
      child: Container(
        width: 72,
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Theme.of(context).cardTheme.color,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: Colors.white.withValues(alpha: 0.06),
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(action.icon, size: 24,
                color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 6),
            Text(
              action.label,
              style: const TextStyle(fontSize: 11),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}
