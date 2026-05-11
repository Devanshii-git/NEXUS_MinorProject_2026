import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  File,
  X,
  CheckCircle2,
  Loader2,
  Sparkles,
} from 'lucide-react';
import DemoBanner from '../components/ui/DemoBanner';

const ACCEPTED_EXTENSIONS = ['.txt', '.pdf', '.docx'];

function getFileIcon(name) {
  const ext = name.split('.').pop().toLowerCase();
  if (ext === 'pdf') return <File size={18} className="text-red-400" />;
  if (ext === 'docx') return <File size={18} className="text-blue-400" />;
  return <FileText size={18} className="text-emerald-400" />;
}

export default function UploadPage({ compact = false }) {
  const [files, setFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [processing, setProcessing] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  }, []);

  const addFiles = useCallback((newFiles) => {
    const valid = Array.from(newFiles).filter((f) => {
      const ext = '.' + f.name.split('.').pop().toLowerCase();
      return ACCEPTED_EXTENSIONS.includes(ext);
    });

    const additions = valid.map((f) => ({
      id: crypto.randomUUID(),
      file: f,
      name: f.name,
      size: f.size,
      status: 'ready',
      progress: 0,
    }));

    setFiles((prev) => [...prev, ...additions]);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
    },
    [addFiles]
  );

  const handleInputChange = (e) => {
    if (e.target.files?.length) addFiles(e.target.files);
  };

  const removeFile = (id) => setFiles((prev) => prev.filter((f) => f.id !== id));

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  };

  const processFiles = async () => {
    setProcessing(true);

    for (let i = 0; i < files.length; i++) {
      const fileItem = files[i];
      const fileId = fileItem.id;

      // Mark as uploading
      setFiles((prev) =>
        prev.map((f) => (f.id === fileId ? { ...f, status: 'uploading', progress: 0 } : f))
      );

      try {
        // Simulated upload (no backend endpoint yet)
        const result = { id: crypto.randomUUID(), filename: fileItem.name, _simulated: true };

        // Show progress animation
        for (let p = 0; p <= 100; p += 20) {
          await new Promise((r) => setTimeout(r, 60));
          setFiles((prev) =>
            prev.map((f) => (f.id === fileId ? { ...f, progress: p } : f))
          );
        }

        setFiles((prev) =>
          prev.map((f) => (f.id === fileId ? { ...f, status: 'processing' } : f))
        );

        await new Promise((r) => setTimeout(r, 400));

        setFiles((prev) =>
          prev.map((f) => (f.id === fileId ? {
            ...f,
            status: 'done',
            progress: 100,
            docId: result?.id || null,
            simulated: result?._simulated || false,
          } : f))
        );
      } catch {
        // Fallback: simulate upload if backend is unreachable
        for (let p = 0; p <= 100; p += 10) {
          await new Promise((r) => setTimeout(r, 80));
          setFiles((prev) =>
            prev.map((f) => (f.id === fileId ? { ...f, progress: p } : f))
          );
        }

        setFiles((prev) =>
          prev.map((f) => (f.id === fileId ? { ...f, status: 'processing' } : f))
        );

        await new Promise((r) => setTimeout(r, 600));

        setFiles((prev) =>
          prev.map((f) => (f.id === fileId ? { ...f, status: 'done', progress: 100, simulated: true } : f))
        );
      }
    }

    setProcessing(false);
  };

  const readyCount = files.filter((f) => f.status === 'ready').length;
  const doneCount = files.filter((f) => f.status === 'done').length;

  if (compact) {
    return (
      <div className="space-y-4">
        <div className="space-y-3">
          <label className="text-xs font-medium block" style={{ color: 'var(--text-secondary)' }}>
            Contact name
          </label>
          <input className="input-field" placeholder="Enter your name" />

          <label className="text-xs font-medium block mt-3" style={{ color: 'var(--text-secondary)' }}>
            How large is your team?
          </label>
          <input className="input-field" placeholder="Team size" />

          <label className="text-xs font-medium block mt-3" style={{ color: 'var(--text-secondary)' }}>
            Which aspects do you need the most support in?
          </label>
          <div className="space-y-2 mt-2">
            {['Data and analytics practice', 'Predictable solutions', 'Data partnerships and integrations', 'All of the above'].map((opt) => (
              <label key={opt} className="flex items-center gap-3 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-gray-300" />
                <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{opt}</span>
              </label>
            ))}
          </div>

          <label className="text-xs font-medium block mt-3" style={{ color: 'var(--text-secondary)' }}>
            When is your target launch?
          </label>
          <input className="input-field" placeholder="Target date" />
        </div>

        <button className="btn-dark w-full mt-4">Submit</button>
        <p className="text-[10px] text-center" style={{ color: 'var(--text-muted)' }}>
          *Your data will remain confidential. Read our privacy policy.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <DemoBanner message="Demo Mode — File upload is simulated. Backend upload endpoint coming soon." />
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="heading-lg">Upload Documents</h1>
        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>
          Drag and drop your requirement documents to get started with AI analysis
        </p>
      </motion.div>

      {/* Drop Zone */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div
          className={`drop-zone relative overflow-hidden ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <div className="relative z-10 flex flex-col items-center gap-4 py-8">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center animate-float"
              style={{
                background: 'linear-gradient(135deg, #c8b4ff, #f5c8d8)',
                boxShadow: '0 8px 30px rgba(200,180,255,0.3)',
              }}
            >
              <Upload size={28} className="text-white" />
            </div>
            <div>
              <p className="text-base font-medium" style={{ color: 'var(--text-primary)' }}>
                Drop your files here or{' '}
                <span className="underline underline-offset-4 cursor-pointer">browse</span>
              </p>
              <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>
                Supports TXT, PDF, DOCX — up to 50MB per file
              </p>
            </div>
          </div>
          <input
            id="fileInput"
            type="file"
            multiple
            accept=".txt,.pdf,.docx"
            onChange={handleInputChange}
            className="hidden"
          />
        </div>
      </motion.div>

      {/* File List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-3"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                Files ({files.length})
              </h3>
              {doneCount === files.length && files.length > 0 && (
                <span className="flex items-center gap-1 text-xs text-emerald-500 font-medium">
                  <CheckCircle2 size={14} /> All processed
                </span>
              )}
            </div>

            {files.map((item, idx) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: idx * 0.05 }}
                className="card flex items-center gap-4 !p-4"
              >
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                     style={{ background: 'var(--bg-secondary)' }}>
                  {getFileIcon(item.name)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                      {item.name}
                    </p>
                    <span className="text-xs shrink-0" style={{ color: 'var(--text-muted)' }}>
                      {formatSize(item.size)}
                    </span>
                  </div>
                  {(item.status === 'uploading' || item.status === 'processing') && (
                    <div className="mt-2 h-1.5 rounded-full overflow-hidden"
                         style={{ background: 'var(--bg-tertiary)' }}>
                      <motion.div
                        className="h-full rounded-full"
                        style={{ background: 'linear-gradient(90deg, #c8b4ff, #f5c8d8)' }}
                        initial={{ width: 0 }}
                        animate={{ width: `${item.progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  )}
                </div>
                <div className="shrink-0">
                  {item.status === 'ready' && (
                    <button onClick={() => removeFile(item.id)} className="p-1.5 rounded-lg btn-ghost">
                      <X size={16} />
                    </button>
                  )}
                  {item.status === 'uploading' && (
                    <Loader2 size={18} className="text-purple-400 animate-spin" />
                  )}
                  {item.status === 'processing' && (
                    <Sparkles size={18} className="text-amber-400 animate-pulse" />
                  )}
                  {item.status === 'done' && (
                    <CheckCircle2 size={18} className="text-emerald-500" />
                  )}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Process button */}
      {readyCount > 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <button
            onClick={processFiles}
            disabled={processing}
            className="btn-dark flex items-center gap-2 disabled:opacity-50"
          >
            {processing ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Processing…
              </>
            ) : (
              <>
                <Sparkles size={16} /> Process {readyCount} file{readyCount > 1 ? 's' : ''} with AI
              </>
            )}
          </button>
        </motion.div>
      )}
    </div>
  );
}
