import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Alert, Grid, Button } from '@mui/material';
import VerifiedIcon from '@mui/icons-material/Verified';
import WarningIcon from '@mui/icons-material/Warning';
import { styled } from '@mui/material/styles';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
}));

interface DocumentAnalyticsProps {
  data: any; // Should be more specific in real implementation
}

export default function DocumentAnalytics({ data }: DocumentAnalyticsProps) {
  if (!data) {
    return (
      <Alert severity="info">
        Processed data will appear here after document processing is complete
      </Alert>
    );
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'success';
    if (confidence >= 0.7) return 'warning';
    return 'error';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.9) return 'High';
    if (confidence >= 0.7) return 'Medium';
    return 'Low';
  };

  const handleExport = async (format: string) => {
    try {
      // In a real implementation, this would call the backend export API
      // For now, we'll just show an alert
      alert(`Export in ${format} format would be triggered here`);
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Processing Results
            </Typography>
            <Box>
              <Button
                variant="contained"
                size="small"
                onClick={() => handleExport('json')}
                sx={{ mr: 1 }}
              >
                Export JSON
              </Button>
              <Button
                variant="contained"
                size="small"
                onClick={() => handleExport('csv')}
                sx={{ mr: 1 }}
              >
                Export CSV
              </Button>
              <Button
                variant="contained"
                size="small"
                onClick={() => handleExport('xlsx')}
              >
                Export Excel
              </Button>
            </Box>
          </Box>
        </Grid>

        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Processing Summary
            </Typography>
            <Box>
              <Typography variant="body2">
                <strong>Fields Detected:</strong> {data.fields?.length || 0}
              </Typography>
              <Typography variant="body2">
                <strong>Text Blocks:</strong> {data.text_blocks?.length || 0}
              </Typography>
              {data.confidence_scores && (
                <Typography variant="body2">
                  <strong>Avg Confidence:</strong> {(data.confidence_scores.overall * 100).toFixed(1)}%
                </Typography>
              )}
            </Box>
          </StyledPaper>
        </Grid>

        <Grid item xs={12} md={8}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Extracted Fields
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Field Name</TableCell>
                    <TableCell>Value</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.fields?.map((field: any, index: number) => (
                    <TableRow key={index}>
                      <TableCell component="th" scope="row">
                        {field.name}
                      </TableCell>
                      <TableCell>{field.value}</TableCell>
                      <TableCell>
                        <Chip label={field.field_type} size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${getConfidenceLabel(field.confidence)} (${(field.confidence * 100).toFixed(1)}%)`}
                          color={getConfidenceColor(field.confidence) as any}
                          size="small"
                          icon={field.confidence >= 0.7 ? <VerifiedIcon /> : <WarningIcon />}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </StyledPaper>
        </Grid>

        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Extracted Text Blocks
            </Typography>
            <Box>
              {data.text_blocks?.map((block: any, index: number) => (
                <Box key={index} mb={1} p={1} bgcolor="grey.50" borderRadius={1}>
                  <Typography variant="body2" component="div">
                    {block.text}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Confidence: {(block.confidence * 100).toFixed(1)}%
                  </Typography>
                </Box>
              ))}
            </Box>
          </StyledPaper>
        </Grid>
      </Grid>
    </Box>
  );
}