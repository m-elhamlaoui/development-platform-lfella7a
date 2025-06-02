import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { bbox, date } = body;

    // Validate request body
    if (!bbox || !date) {
      return NextResponse.json(
        { message: 'Missing required parameters' },
        { status: 400 }
      );
    }

    // Get the path to our Python script
    const scriptPath = path.join(process.cwd(), 'GIS', 'cyfi', 'core', 'analyze_cli.py');

    return new Promise((resolve) => {
      // Run Python script
      const pythonProcess = spawn('python', [
        scriptPath,
        JSON.stringify({
          bbox,
          date,
          grid_size: 0.001
        })
      ]);

      let result = '';
      let error = '';

      pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
        console.error('Python error:', data.toString());
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error('Python process error:', error);
          resolve(
            NextResponse.json(
              { message: 'Analysis failed', details: error },
              { status: 500 }
            )
          );
          return;
        }

        try {
          const analysisResult = JSON.parse(result);
          resolve(NextResponse.json(analysisResult));
        } catch (e) {
          console.error('Failed to parse Python output:', e);
          resolve(
            NextResponse.json(
              { message: 'Failed to parse analysis results' },
              { status: 500 }
            )
          );
        }
      });
    });
  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { message: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 