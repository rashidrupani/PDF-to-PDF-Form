import { useState, useCallback } from 'react';
import { Typography, Container, Box, Paper, Grid, Card, CardContent, CardHeader, Alert } from '@mui/material';
import { styled } from '@mui/material/styles';
import DocumentUpload from '../components/DocumentUpload';
import ProcessingStatus from '../components/ProcessingStatus';
import DocumentAnalytics from '../components/DocumentAnalytics';

const StyledContainer = styled(Container)(({ theme }) => ({
  paddingTop: theme.spacing(4),
  paddingBottom: theme.spacing(4),
}));

export default function Home() {
  const [processingJob, setProcessingJob] = useState<any>(null);
  const [processedData, setProcessedData] = useState<any>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileUpload = useCallback(async (files: File[]) => {
    if (files.length === 0) return;

    const file = files[0];
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Upload document
      const uploadResponse = await fetch('/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const jobData = await uploadResponse.json();
      setProcessingJob(jobData);

      // Poll for processing status
      const pollStatus = async () => {
        const statusResponse = await fetch(`/documents/${jobData.job_id}/status`);
        const statusData = await statusResponse.json();

        if (statusData.status === 'completed') {
          // Get full document data
          const docResponse = await fetch(`/documents/${jobData.job_id}`);
          const docData = await docResponse.json();

          setProcessedData(docData.result);
          setProcessingJob({ ...jobData, ...statusData });
        } else if (statusData.status === 'failed') {
          setUploadError(statusData.error || 'Processing failed');
          setProcessingJob(statusData);
        } else {
          // Continue polling
          setTimeout(pollStatus, 2000);
        }
      };

      // Start polling
      setTimeout(pollStatus, 1000);

    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error.message || 'Upload failed');
    }
  }, []);

  return (
    <StyledContainer maxWidth="xl">
      <Box textAlign="center" mb={4}>
        <Typography variant="h2" component="h1" gutterBottom>
          Simple AI Document Processor
        </Typography>
        <Typography variant="h5" color="text.secondary">
          Intelligent document processing with OCR, form field detection, and validation
        </Typography>
      </Box>

      {uploadError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {uploadError}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Upload Document" />
            <CardContent>
              <DocumentUpload onFilesUploaded={handleFileUpload} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Processing Status" />
            <CardContent>
              <ProcessingStatus job={processingJob} />
            </CardContent>
          </Card>
        </Grid>

        {processedData && (
          <Grid item xs={12}>
            <Card>
              <CardHeader title="Extracted Data" />
              <CardContent>
                <DocumentAnalytics data={processedData} />
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </StyledContainer>
  );
}