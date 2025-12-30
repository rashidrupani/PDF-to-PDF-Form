import { Box, Typography, LinearProgress, Chip, Alert } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { styled } from '@mui/material/styles';

const StatusContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
}));

interface ProcessingStatusProps {
  job: any; // Should be more specific in real implementation
}

export default function ProcessingStatus({ job }: ProcessingStatusProps) {
  if (!job) {
    return (
      <Alert severity="info">
        Upload a document to begin processing
      </Alert>
    );
  }

  const getStatusColor = () => {
    switch (job.status) {
      case 'processing':
        return 'warning';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'info';
    }
  };

  const getStatusIcon = () => {
    switch (job.status) {
      case 'completed':
        return <CheckCircleIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return null;
    }
  };

  return (
    <StatusContainer>
      <Box display="flex" alignItems="center" mb={2}>
        {getStatusIcon()}
        <Box ml={1}>
          <Chip
            label={job.status?.toUpperCase()}
            color={getStatusColor() as any}
            size="small"
          />
          <Typography variant="h6" component="div" sx={{ ml: 1, display: 'inline' }}>
            {job.status === 'processing'
              ? `Processing: ${job.progress || 0}% complete`
              : job.status === 'completed'
                ? 'Processing completed successfully!'
                : job.error || 'Processing failed'}
          </Typography>
        </Box>
      </Box>

      {job.status === 'processing' && (
        <Box>
          <LinearProgress
            variant="determinate"
            value={job.progress || 0}
            sx={{ mb: 1 }}
          />
          <Typography variant="body2" color="text.secondary">
            {job.progress || 0}% complete
          </Typography>
        </Box>
      )}

      {job.status === 'completed' && (
        <Alert severity="success">
          Document processing completed successfully!
        </Alert>
      )}

      {job.status === 'failed' && (
        <Alert severity="error">
          {job.error || 'An error occurred during processing'}
        </Alert>
      )}

      {job.original_filename && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Processing: {job.original_filename}
        </Typography>
      )}
    </StatusContainer>
  );
}