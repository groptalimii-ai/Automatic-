/**
 * 📱 Digital Factory Mobile App
 * ================================
 * تطبيق موبايل لإدارة المصنع
 * 
 * Tech Stack: React Native + Expo
 */

import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  SafeAreaView, StatusBar, RefreshControl
} from 'react-native';
import { Card, Button, Badge, ProgressBar } from 'react-native-paper';

// API Base URL
const API_URL = 'http://YOUR_SERVER_IP:5000';

export default function App() {
  const [agents, setAgents] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState({});
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const agentsRes = await fetch(`${API_URL}/api/agents`);
      const agentsData = await agentsRes.json();
      setAgents(agentsData);

      const jobsRes = await fetch(`${API_URL}/api/jobs`);
      const jobsData = await jobsRes.json();
      setJobs(jobsData);

      const statsRes = await fetch(`${API_URL}/api/status`);
      const statsData = await statsRes.json();
      setStats(statsData);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    fetchData().then(() => setRefreshing(false));
  };

  const startProduction = async (mode, niche) => {
    try {
      await fetch(`${API_URL}/api/produce`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, niche })
      });
      alert('Production started!');
    } catch (error) {
      alert('Error starting production');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#667eea" />

      <View style={styles.header}>
        <Text style={styles.headerTitle}>🏭 Digital Factory</Text>
        <Text style={styles.headerSubtitle}>مصنع المنتجات الرقمية</Text>
      </View>

      <ScrollView refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
        <View style={styles.statsContainer}>
          <Card style={styles.statCard}>
            <Card.Content>
              <Text style={styles.statNumber}>{jobs.length}</Text>
              <Text style={styles.statLabel}>إجمالي المنتجات</Text>
            </Card.Content>
          </Card>
          <Card style={styles.statCard}>
            <Card.Content>
              <Text style={styles.statNumber}>
                {jobs.filter(j => j.status === 'completed').length}
              </Text>
              <Text style={styles.statLabel}>مكتملة</Text>
            </Card.Content>
          </Card>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚡ إنتاج سريع</Text>
          <View style={styles.buttonRow}>
            <TouchableOpacity 
              style={[styles.actionButton, { backgroundColor: '#667eea' }]}
              onPress={() => startProduction('ebook', 'productivity')}>
              <Text style={styles.buttonText}>📚 كتاب</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.actionButton, { backgroundColor: '#10b981' }]}
              onPress={() => startProduction('template', 'CRM')}>
              <Text style={styles.buttonText}>📋 قالب</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={[styles.actionButton, { backgroundColor: '#f59e0b' }]}
              onPress={() => startProduction('fitness', 'Build Muscle')}>
              <Text style={styles.buttonText}>💪 لياقة</Text>
            </TouchableOpacity>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🤖 حالة الوكلاء</Text>
          {agents.map((agent, index) => (
            <Card key={index} style={styles.agentCard}>
              <Card.Content style={styles.agentRow}>
                <Text style={styles.agentIcon}>{agent.icon}</Text>
                <View style={styles.agentInfo}>
                  <Text style={styles.agentName}>{agent.name}</Text>
                  <Badge style={[styles.agentBadge, { 
                    backgroundColor: agent.status === 'active' ? '#10b981' : '#6b7280' 
                  }]}>{agent.status}</Badge>
                </View>
              </Card.Content>
            </Card>
          ))}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📋 المهام الأخيرة</Text>
          {jobs.slice(0, 5).map((job, index) => (
            <Card key={index} style={styles.jobCard}>
              <Card.Content>
                <View style={styles.jobHeader}>
                  <Text style={styles.jobType}>{job.type}</Text>
                  <Badge style={[styles.jobBadge, { 
                    backgroundColor: job.status === 'completed' ? '#10b981' : 
                                     job.status === 'failed' ? '#ef4444' : '#f59e0b'
                  }]}>{job.status}</Badge>
                </View>
                <Text style={styles.jobNiche}>{job.niche}</Text>
              </Card.Content>
            </Card>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f3f4f6' },
  header: { backgroundColor: '#667eea', padding: 20, paddingTop: 40 },
  headerTitle: { color: 'white', fontSize: 24, fontWeight: 'bold', textAlign: 'center' },
  headerSubtitle: { color: 'rgba(255,255,255,0.8)', fontSize: 14, textAlign: 'center', marginTop: 4 },
  statsContainer: { flexDirection: 'row', padding: 16, gap: 12 },
  statCard: { flex: 1, elevation: 2 },
  statNumber: { fontSize: 28, fontWeight: 'bold', color: '#667eea', textAlign: 'center' },
  statLabel: { fontSize: 12, color: '#6b7280', textAlign: 'center', marginTop: 4 },
  section: { padding: 16 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 12, color: '#1f2937' },
  buttonRow: { flexDirection: 'row', gap: 10 },
  actionButton: { flex: 1, padding: 16, borderRadius: 12, alignItems: 'center' },
  buttonText: { color: 'white', fontWeight: 'bold', fontSize: 14 },
  agentCard: { marginBottom: 8, elevation: 1 },
  agentRow: { flexDirection: 'row', alignItems: 'center' },
  agentIcon: { fontSize: 24, marginRight: 12 },
  agentInfo: { flex: 1, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  agentName: { fontSize: 14, fontWeight: '600' },
  agentBadge: { alignSelf: 'center' },
  jobCard: { marginBottom: 8, elevation: 1 },
  jobHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 },
  jobType: { fontWeight: 'bold', fontSize: 14 },
  jobBadge: { alignSelf: 'center' },
  jobNiche: { color: '#6b7280', fontSize: 12 },
});
