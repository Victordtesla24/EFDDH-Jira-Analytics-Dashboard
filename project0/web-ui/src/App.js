import React from 'react';
import { Container, CssBaseline, Typography, AppBar, Toolbar, Button, Paper, Grid, TextField, Tooltip, IconButton } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import InfoIcon from '@material-ui/icons/Info';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  appBar: {
    marginBottom: theme.spacing(4),
  },
  title: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(4),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  form: {
    '& > *': {
      margin: theme.spacing(1),
      width: '100%',
    },
  },
  button: {
    marginTop: theme.spacing(2),
  },
  infoButton: {
    marginLeft: theme.spacing(1),
  },
}));

function App() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar position="static" className={classes.appBar}>
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
            AI Assistant
          </Typography>
          <Button color="inherit">Login</Button>
        </Toolbar>
      </AppBar>
      <Container>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <Typography variant="h4" gutterBottom>
                Welcome to the AI Assistant
              </Typography>
              <Typography variant="body1" gutterBottom>
                Optimize your resume, analyze job descriptions, and handle errors with our state-of-the-art AI assistant.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12}>
            <Paper className={classes.paper}>
              <form className={classes.form} noValidate autoComplete="off">
                <TextField id="outlined-basic" label="Resume" variant="outlined" multiline rows={4} />
                <TextField id="outlined-basic" label="Job Description" variant="outlined" multiline rows={4} />
                <Tooltip title="Click to analyze your resume against the job description">
                  <Button variant="contained" color="primary" className={classes.button}>
                    Analyze
                  </Button>
                </Tooltip>
              </form>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </div>
  );
}

export default App;