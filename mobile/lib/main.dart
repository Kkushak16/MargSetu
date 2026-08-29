/// MargSetu Flutter Field App (Member C - Prompt 3)
/// SIH26002 - Smart Logistics & Accessibility Platform

import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import 'sync_manager.dart';

void main() {
  runApp(const MargSetuFieldApp());
}

class MargSetuFieldApp extends StatelessWidget {
  const MargSetuFieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MargSetu Field App',
      theme: ThemeData.dark().copyWith(
        primaryColor: const Color(0xFF0284C7),
        scaffoldBackgroundColor: const Color(0xFF0F172A),
      ),
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = const [
    MapScreen(),
    ReportScreen(),
    SyncStatusScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        backgroundColor: const Color(0xFF1E293B),
        selectedItemColor: const Color(0xFF38BDF8),
        unselectedItemColor: const Color(0xFF94A3B8),
        onTap: (index) => setState(() => _selectedIndex = index),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.map), label: 'Hazard Map'),
          BottomNavigationBarItem(icon: Icon(Icons.add_location_alt), label: 'Report Hazard'),
          BottomNavigationBarItem(icon: Icon(Icons.sync), label: 'Sync Status'),
        ],
      ),
    );
  }
}

/// Screen 1: Offline GeoJSON Hazard Map
class MapScreen extends StatelessWidget {
  const MapScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🏔️ Offline Hazard Corridor Map')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  Text('🟢 SAFE (<0.35)', style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold)),
                  Text('🟡 WARNING', style: TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)),
                  Text('🔴 BLOCKED (≥0.70)', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF020617),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: ListView(
                  padding: const EdgeInsets.all(12),
                  children: const [
                    ListTile(
                      leading: Icon(Icons.circle, color: Colors.green),
                      title: Text('NH10_SEG_001 (Siliguri -> Sevoke)'),
                      subtitle: Text('Hazard: 10% | Status: SAFE | Speed: 50 km/h'),
                    ),
                    Divider(color: Color(0xFF334155)),
                    ListTile(
                      leading: Icon(Icons.circle, color: Colors.amber),
                      title: Text('NH10_SEG_002 (Sevoke -> Kalimpong)'),
                      subtitle: Text('Hazard: 45% | Status: WARNING_SLOW'),
                    ),
                    Divider(color: Color(0xFF334155)),
                    ListTile(
                      leading: Icon(Icons.circle, color: Colors.red),
                      title: Text('NH10_SEG_003 (Kalimpong -> Rangpo)'),
                      subtitle: Text('Hazard: 82% | Status: CRITICAL_AVOID (BLOCKED)'),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Screen 2: Offline-First Report Submission Form
class ReportScreen extends StatefulWidget {
  const ReportScreen({super.key});

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  String _reportType = 'blockage';
  final _reporterController = TextEditingController(text: 'FIELD_DRIVER_NER');

  void _submitReport() async {
    final report = FieldReport(
      id: const Uuid().v4(),
      reporterId: _reporterController.text,
      reportType: _reportType,
      lat: 27.1764,
      lng: 88.5341,
      submittedAt: DateTime.now().toIso8601String(),
    );

    await FlutterSyncManager.instance.saveReportOffline(report);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✓ Report saved to offline SQLite queue! Auto-syncing...'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('📱 Submit Field Hazard Report')),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _reporterController,
              decoration: const InputDecoration(labelText: 'Reporter / Driver ID', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _reportType,
              decoration: const InputDecoration(labelText: 'Report Hazard Type', border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: 'blockage', child: Text('🚧 Complete Road Blockage')),
                DropdownMenuItem(value: 'flood', child: Text('🌊 Flash Flood / Mudslide')),
                DropdownMenuItem(value: 'crack', child: Text('⚡ Fissure / Rockfall')),
                DropdownMenuItem(value: 'clear', child: Text('✅ Road Reopened')),
              ],
              onChanged: (val) => setState(() => _reportType = val!),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.save),
              label: const Text('Save Offline & Sync'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFDC2626),
                padding: const EdgeInsets.all(16),
              ),
              onPressed: _submitReport,
            ),
          ],
        ),
      ),
    );
  }
}

/// Screen 3: Sync Status & Queue Manager
class SyncStatusScreen extends StatefulWidget {
  const SyncStatusScreen({super.key});

  @override
  State<SyncStatusScreen> createState() => _SyncStatusScreenState();
}

class _SyncStatusScreenState extends State<SyncStatusScreen> {
  int _pendingCount = 0;

  @override
  void initState() {
    super.initState();
    _loadPendingCount();
  }

  void _loadPendingCount() async {
    final count = await FlutterSyncManager.instance.getPendingCount();
    setState(() => _pendingCount = count);
  }

  void _syncNow() async {
    await FlutterSyncManager.instance.syncUp();
    _loadPendingCount();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sync completed!')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🔄 Offline Sync Status')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                _pendingCount > 0 ? Icons.sync_problem : Icons.check_circle,
                size: 80,
                color: _pendingCount > 0 ? Colors.amber : Colors.green,
              ),
              const SizedBox(height: 20),
              Text(
                _pendingCount > 0 ? '$_pendingCount Reports Pending Sync' : 'All Field Data Synced',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 30),
              ElevatedButton.icon(
                icon: const Icon(Icons.sync),
                label: const Text('Sync Now'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0284C7),
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
                onPressed: _syncNow,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
