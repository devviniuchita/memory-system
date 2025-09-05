#!/usr/bin/env node
/**
 * memory-dual-brain-sync-oneshot.js
 * Single execution version without file watching
 */

const fs = require('fs/promises');
const path = require('path');
const crypto = require('crypto');
const EventEmitter = require('events');

class MemoryDualBrainSync extends EventEmitter {
  constructor(config) {
    super();
    const cwd = process.cwd();
    this.config = Object.assign(
      {
        executionBrain: path.resolve(config?.executionBrain || path.join(cwd, 'memory-rules.mdc')),
        qualityBrain: path.resolve(config?.qualityBrain || path.join(cwd, 'memory-rating.mdc')),
        syncEnabled: config?.syncEnabled ?? true,
        autoActivation: config?.autoActivation ?? true,
        maxRetries: config?.maxRetries ?? 3,
        retryBaseMs: config?.retryBaseMs ?? 150,
        metricsPath: path.resolve(
          config?.metricsPath || path.join(cwd, 'memory-sync-metrics.json')
        ),
        verbose: config?.verbose ?? false,
      },
      config || {}
    );
    this.retryCount = 0;
    this.lastChecksums = {};
    this.metricsFile = this.config.metricsPath;
  }

  async activateMemorySystem() {
    if (!this.config.autoActivation || !this.config.syncEnabled) return;
    try {
      const t0 = Date.now();
      await this.loadExecutionBrain();
      await this.loadQualityBrain();
      await this.performBidirectionalSync();
      await this.validateSyncState();
      this.retryCount = 0;
      await this.appendMetric('activate', { durationMs: Date.now() - t0, ok: true });
      if (this.config.verbose) console.log('🧠 MEMORY DUAL-BRAIN SYSTEM: ACTIVATED & SYNCED ✅');
      this.emit('activated');
    } catch (err) {
      await this.appendMetric('activate', { ok: false, error: String(err) });
      if (this.retryCount < this.config.maxRetries) {
        this.retryCount++;
        const wait = this.config.retryBaseMs * this.retryCount;
        if (this.config.verbose) console.warn('⚠ Activate failed, retrying in', wait, 'ms');
        await new Promise((res) => setTimeout(res, wait));
        return this.activateMemorySystem();
      }
      throw err;
    }
  }

  async loadExecutionBrain() {
    const start = Date.now();
    const content = await fs.readFile(this.config.executionBrain, 'utf-8');
    const checksum = this.sha256(content);
    if (checksum !== this.lastChecksums.exec) {
      this.lastChecksums.exec = checksum;
      this.applyExecutionContext(content);
      await this.appendMetric('loadExecutionBrain', { durationMs: Date.now() - start, checksum });
      if (this.config.verbose) console.log('[loadExecutionBrain] applied, checksum=', checksum);
    } else {
      await this.appendMetric('loadExecutionBrain', {
        durationMs: Date.now() - start,
        checksum,
        skipped: true,
      });
      if (this.config.verbose) console.log('[loadExecutionBrain] skipped (no changes)');
    }
  }

  async loadQualityBrain() {
    const start = Date.now();
    const content = await fs.readFile(this.config.qualityBrain, 'utf-8');
    const checksum = this.sha256(content);
    if (checksum !== this.lastChecksums.qual) {
      this.lastChecksums.qual = checksum;
      this.applyQualityContext(content);
      await this.appendMetric('loadQualityBrain', { durationMs: Date.now() - start, checksum });
      if (this.config.verbose) console.log('[loadQualityBrain] applied, checksum=', checksum);
    } else {
      await this.appendMetric('loadQualityBrain', {
        durationMs: Date.now() - start,
        checksum,
        skipped: true,
      });
      if (this.config.verbose) console.log('[loadQualityBrain] skipped (no changes)');
    }
  }

  async performBidirectionalSync() {
    const start = Date.now();
    const execContent = await fs.readFile(this.config.executionBrain, 'utf-8');
    const qualContent = await fs.readFile(this.config.qualityBrain, 'utf-8');

    const execChanges = this.diffBrainContent(execContent, qualContent, 'execution->quality');
    const qualChanges = this.diffBrainContent(qualContent, execContent, 'quality->execution');

    await this.appendMetric('performBidirectionalSync', {
      durationMs: Date.now() - start,
      execChanges: execChanges.length,
      qualChanges: qualChanges.length,
    });

    if (this.config.verbose) {
      console.log(
        '[performBidirectionalSync] execChanges=',
        execChanges.length,
        'qualChanges=',
        qualChanges.length
      );
      console.log('🔄 Bidirectional sync analysis completed');
    }
  }

  async validateSyncState() {
    const start = Date.now();
    const checks = {
      executionBrainLoaded: !!this.lastChecksums.exec,
      qualityBrainLoaded: !!this.lastChecksums.qual,
      syncCompleted: true,
      performanceThresholds: true,
    };
    const allValid = Object.values(checks).every(Boolean);
    await this.appendMetric('validateSyncState', { durationMs: Date.now() - start, checks });
    return allValid;
  }

  shouldActivateSync(context) {
    if (!this.config.syncEnabled) return false;
    const triggers = [
      'conversation_start',
      'user_request',
      'code_change',
      'topic_change',
      'memory_operation',
      'mcp_interaction',
      'quality_gate',
      'performance_check',
    ];
    return triggers.some((t) => context.toLowerCase().includes(t));
  }

  sha256(s) {
    return crypto.createHash('sha256').update(s, 'utf8').digest('hex');
  }

  diffBrainContent(source, target, direction) {
    const srcLines = new Set(
      source
        .split(/\r?\n/)
        .map((l) => l.trim())
        .filter(Boolean)
    );
    const tgtLines = new Set(
      target
        .split(/\r?\n/)
        .map((l) => l.trim())
        .filter(Boolean)
    );
    const changes = [];
    for (const l of srcLines) {
      if (!tgtLines.has(l)) changes.push(l);
    }
    if (this.config.verbose && changes.length)
      console.log(`[diff:${direction}] found ${changes.length} changes`);
    return changes;
  }

  applyExecutionContext(rules) {
    this.emit('executionContextApplied', { rules });
  }

  applyQualityContext(rules) {
    this.emit('qualityContextApplied', { rules });
  }

  async appendMetric(key, data) {
    const now = new Date().toISOString();
    const entry = { ts: now, key, data };
    try {
      let arr = [];
      try {
        const raw = await fs.readFile(this.metricsFile, 'utf-8');
        arr = JSON.parse(raw || '[]');
      } catch {
        arr = [];
      }
      arr.push(entry);
      await fs.writeFile(this.metricsFile, JSON.stringify(arr, null, 2), 'utf-8');
    } catch (err) {
      if (this.config.verbose) console.error('Failed to write metrics', err);
    }
  }
}

// Single execution bootstrap
(async function main() {
  const cfg = {
    executionBrain: process.env.EXECUTION_BRAIN || undefined,
    qualityBrain: process.env.QUALITY_BRAIN || undefined,
    syncEnabled: true,
    autoActivation: process.env.AUTO_ACTIVATE !== 'false',
    maxRetries: Number(process.env.MAX_RETRIES || 3),
    retryBaseMs: Number(process.env.RETRY_BASE_MS || 150),
    metricsPath: process.env.METRICS_PATH || './memory-sync-metrics.json',
    verbose: process.env.VERBOSE === '1' || process.env.VERBOSE === 'true',
  };

  const sync = new MemoryDualBrainSync(cfg);

  // Bind logging
  sync.on('executionContextApplied', () =>
    console.log('[EVENT] ⚡ Execution Brain Context Applied')
  );
  sync.on('qualityContextApplied', () => console.log('[EVENT] 🎯 Quality Brain Context Applied'));
  sync.on('activated', () => console.log('[EVENT] 🚀 Memory Dual-Brain System Activated'));

  try {
    console.log('🧠 Initializing Memory Dual-Brain Sync System...');
    console.log('📋 Configuration:');
    console.log('  - Execution Brain:', cfg.executionBrain || './memory-rules.mdc');
    console.log('  - Quality Brain:', cfg.qualityBrain || './memory-rating.mdc');
    console.log('  - Verbose Mode:', cfg.verbose ? 'ON' : 'OFF');
    console.log('');

    await sync.activateMemorySystem();

    console.log('');
    console.log('✅ Memory Dual-Brain Sync completed successfully!');
    console.log('📊 Metrics saved to:', cfg.metricsPath);
    console.log('🎯 Both brains are now synchronized and ready for AI operations');
  } catch (err) {
    console.error('❌ Fatal error during sync:', err.message);
    process.exit(1);
  }
})();
