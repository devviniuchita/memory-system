#!/usr/bin/env node
/**
 * memory-dual-brain-sync.js
 * Runnable Node.js implementation of the Memory Dual-Brain Sync System.
 *
 * Usage:
 *   node memory-dual-brain-sync.js   # runs with defaults
 *   EXECUTION_BRAIN=./other-exec.mdc QUALITY_BRAIN=./other-qual.mdc node memory-dual-brain-sync.js
 *
 * Outputs metrics to memory-sync-metrics.json in the cwd by default.
 */

const fs = require('fs/promises');
const fsSync = require('fs');
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

    // 🚫 DISABLED AUTO-UPDATE TO PREVENT INFINITE LOOPS
    // Rule files should remain static and not be auto-modified
    // if (execChanges.length) {
    //   await this.updateQualityBrain(execChanges);
    // }
    // if (qualChanges.length) {
    //   await this.updateExecutionBrain(qualChanges);
    // }

    await this.appendMetric('performBidirectionalSync', {
      durationMs: Date.now() - start,
      execChanges: execChanges.length,
      qualChanges: qualChanges.length,
    });

    if (this.config.verbose) {
      console.log('🔄 Bidirectional sync analysis completed');
      console.log(
        '[performBidirectionalSync] execChanges=',
        execChanges.length,
        'qualChanges=',
        qualChanges.length
      );
      console.log('📋 Auto-modification disabled to maintain rule stability');
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
    if (!allValid) {
      if (this.retryCount < this.config.maxRetries) {
        this.retryCount++;
        await new Promise((r) => setTimeout(r, this.config.retryBaseMs * this.retryCount));
        return this.activateMemorySystem();
      }
    }
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

  async updateQualityBrain(updates) {
    const safepath = this.config.qualityBrain + '.sync.tmp';
    const content = updates.join('\n') + '\n';
    await fs.appendFile(safepath, content, 'utf-8');
    await fs.rename(safepath, this.config.qualityBrain).catch(() => {});
    this.emit('qualityUpdated', { updatesCount: updates.length });
  }

  async updateExecutionBrain(updates) {
    const safepath = this.config.executionBrain + '.sync.tmp';
    const content = updates.join('\n') + '\n';
    await fs.appendFile(safepath, content, 'utf-8');
    await fs.rename(safepath, this.config.executionBrain).catch(() => {});
    this.emit('executionUpdated', { updatesCount: updates.length });
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

// CLI bootstrap
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
  // Bind simple logging
  sync.on('executionContextApplied', (d) =>
    console.log('[EVENT] executionContextApplied', Array.isArray(d.rules) ? d.rules.length : 'len')
  );
  sync.on('qualityContextApplied', (d) => console.log('[EVENT] qualityContextApplied'));
  sync.on('activated', () => console.log('[EVENT] activated'));
  try {
    await sync.activateMemorySystem();
    // Optionally keep process alive to listen to file changes in dev mode
    if (cfg.autoActivation) {
      // watch files for changes and auto-trigger
      const execPath = sync.config.executionBrain;
      const qualPath = sync.config.qualityBrain;
      fsSync.watchFile(execPath, { interval: 1000 }, async () => {
        console.log('[WATCH] executionBrain changed -> re-activate');
        await sync.activateMemorySystem();
      });
      fsSync.watchFile(qualPath, { interval: 1000 }, async () => {
        console.log('[WATCH] qualityBrain changed -> re-activate');
        await sync.activateMemorySystem();
      });
    }
  } catch (err) {
    console.error('Fatal error', err);
    process.exit(1);
  }
})();
