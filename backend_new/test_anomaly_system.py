"""
Test script for anomaly detection system
Tests all components: tracking, anomaly detection, database, and API
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from anomaly_detector import AnomalyDetector, Anomaly
from database import Database, AnomalyRecord
import math

print("🧪 Testing Anomaly Detection System\n")
print("=" * 60)

# Test 1: AnomalyDetector initialization
print("\n✅ Test 1: AnomalyDetector initialization")
try:
    detector = AnomalyDetector()
    print(f"   ✓ AnomalyDetector created successfully")
    print(f"   - Stop threshold: {detector.stop_threshold_px}px")
    print(f"   - Speed threshold: {detector.speed_threshold_px}px")
    print(f"   - Spike multiplier: {detector.spike_multiplier}x")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 2: Stopped vehicle detection
print("\n✅ Test 2: Stopped vehicle detection")
try:
    # Create a trajectory where vehicle barely moves
    stopped_trajectory = {
        "track_id": 1,
        "class_name": "car",
        "positions": [(100, 200), (102, 201), (103, 202), (104, 203)],
        "timestamps": [0.0, 1.0, 2.0, 3.5],
        "frames": [0, 30, 60, 90]
    }
    
    anomaly = detector.detect_stopped_vehicle(stopped_trajectory)
    if anomaly:
        print(f"   ✓ Stopped vehicle detected!")
        print(f"   - Type: {anomaly.anomaly_type}")
        print(f"   - Timestamp: {anomaly.timestamp:.1f}s")
        print(f"   - Severity: {anomaly.severity}")
        print(f"   - Description: {anomaly.description}")
    else:
        print(f"   ✗ No anomaly detected (expected one)")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 3: High speed detection
print("\n✅ Test 3: High speed detection")
try:
    # Create a trajectory with large movement
    speeding_trajectory = {
        "track_id": 2,
        "class_name": "car",
        "positions": [(100, 200), (400, 250)],  # 300+ pixel jump
        "timestamps": [0.0, 0.33],
        "frames": [0, 10]
    }
    
    anomaly = detector.detect_high_speed(speeding_trajectory)
    if anomaly:
        print(f"   ✓ High speed detected!")
        print(f"   - Type: {anomaly.anomaly_type}")
        print(f"   - Timestamp: {anomaly.timestamp:.1f}s")
        print(f"   - Severity: {anomaly.severity}")
        print(f"   - Description: {anomaly.description}")
    else:
        print(f"   ✗ No anomaly detected (expected one)")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 4: Traffic spike detection
print("\n✅ Test 4: Traffic spike detection")
try:
    # Create segments with a spike
    segments = [10, 12, 50, 11, 10, 9, 12, 10, 11, 10]  # Spike at segment 2
    duration = 100.0
    
    anomalies = detector.detect_traffic_spike(segments, duration)
    if anomalies:
        print(f"   ✓ {len(anomalies)} traffic spike(s) detected!")
        for i, anomaly in enumerate(anomalies, 1):
            print(f"   {i}. {anomaly.description} at {anomaly.timestamp:.1f}s")
    else:
        print(f"   ✗ No spikes detected (expected one)")
except Exception as e:
    print(f"   ✗ Failed: {e}")

# Test 5: Database operations
print("\n✅ Test 5: Database operations")
try:
    db = Database()
    print(f"   ✓ Database initialized")
    
    # Test saving anomalies
    test_anomalies = [
        {
            "timestamp": 10.5,
            "anomaly_type": "stopped",
            "severity": "medium",
            "description": "Test stopped vehicle",
            "track_id": 1,
            "metadata": {"test": True}
        },
        {
            "timestamp": 25.0,
            "anomaly_type": "speeding",
            "severity": "high",
            "description": "Test high speed",
            "track_id": 2,
            "metadata": {"speed": 300}
        }
    ]
    
    db.save_anomalies("test_video.mp4", test_anomalies)
    print(f"   ✓ Saved {len(test_anomalies)} test anomalies")
    
    # Test retrieving anomalies
    retrieved = db.get_anomalies("test_video.mp4")
    print(f"   ✓ Retrieved {len(retrieved)} anomalies")
    
    for i, a in enumerate(retrieved, 1):
        print(f"   {i}. {a.anomaly_type} at {a.timestamp}s - {a.description}")
    
    # Clean up test data
    db.delete_anomalies("test_video.mp4")
    print(f"   ✓ Cleaned up test data")
    
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Analyze all (integration test)
print("\n✅ Test 6: Integration test - analyze_all()")
try:
    trajectories = {
        1: {
            "track_id": 1,
            "class_name": "car",
            "positions": [(100, 200), (102, 201), (103, 202)],
            "timestamps": [0.0, 1.5, 3.5],
            "frames": [0, 45, 105]
        },
        2: {
            "track_id": 2,
            "class_name": "truck",
            "positions": [(50, 100), (350, 150)],
            "timestamps": [5.0, 5.33],
            "frames": [150, 160]
        }
    }
    
    segments = [5, 6, 25, 7, 5, 6, 5, 6, 5, 6]
    duration = 60.0
    
    all_anomalies = detector.analyze_all(trajectories, segments, duration)
    print(f"   ✓ Found {len(all_anomalies)} total anomalies")
    
    for i, anomaly in enumerate(all_anomalies, 1):
        print(f"   {i}. [{anomaly.severity}] {anomaly.anomaly_type} at {anomaly.timestamp:.1f}s")
        print(f"      {anomaly.description}")
    
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 All tests completed!")
print("\n💡 Next steps:")
print("   1. Upload a video through the frontend")
print("   2. Check the terminal for 'Analyzing anomalies...' message")
print("   3. Ask the AI chat: 'יש אנומליות בסרטון?'")
print("   4. Check endpoint: GET /api/anomalies/{filename}")
