import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

// Convert exec to Promise-based
const execPromise = promisify(exec);

interface RequestBody {
  bboxCoords: [number, number, number, number]; // [west, south, east, north]
  timeInterval: [string, string]; // [startDate, endDate]
  dataSource?: string; // satellite data source
}

export async function POST(request: NextRequest) {
  let configPath: string | null = null;
  
  try {
    const body: RequestBody = await request.json();
    
    console.log('Received water quality analysis request for bbox:', body.bboxCoords);
    console.log('Time interval:', body.timeInterval);
    console.log('Data source:', body.dataSource || 'sentinel2 (default)');
    
    // Validate input
    if (!body.bboxCoords || !Array.isArray(body.bboxCoords) || body.bboxCoords.length !== 4) {
      return NextResponse.json(
        { error: 'Invalid bounding box coordinates' },
        { status: 400 }
      );
    }

    if (!body.timeInterval || !Array.isArray(body.timeInterval) || body.timeInterval.length !== 2) {
      return NextResponse.json(
        { error: 'Invalid time interval' },
        { status: 400 }
      );
    }
    
    // Validate data source if provided
    const validDataSources = [
      'sentinel2', 'sentinel2_l1c',
      'landsat8', 'landsat8_l1', 'landsat7', 'landsat5',
      'hls', 'modis'
    ];
    
    if (body.dataSource && !validDataSources.includes(body.dataSource)) {
      return NextResponse.json(
        { error: `Invalid data source. Must be one of: ${validDataSources.join(', ')}` },
        { status: 400 }
      );
    }
    
    // Validate coordinates range
    const [west, south, east, north] = body.bboxCoords;
    if (!(
      -180 <= west && west <= 180 &&
      -90 <= south && south <= 90 &&
      -180 <= east && east <= 180 &&
      -90 <= north && north <= 90
    )) {
      return NextResponse.json(
        { error: 'Coordinates out of range. Longitude must be between -180 and 180, latitude between -90 and 90.' },
        { status: 400 }
      );
    }
    
    // Check if bounding box is too large
    const widthDeg = Math.abs(east - west);
    const heightDeg = Math.abs(north - south);
    
    if (widthDeg > 10 || heightDeg > 10) {
      return NextResponse.json(
        { error: `Bounding box too large: ${widthDeg.toFixed(2)}° x ${heightDeg.toFixed(2)}°. Please select a smaller area (max: 10° x 10°).` },
        { status: 400 }
      );
    }
    
    // Check if bounding box is too small
    if (widthDeg < 0.001 || heightDeg < 0.001) {
      return NextResponse.json(
        { error: `Bounding box too small: ${widthDeg.toFixed(6)}° x ${heightDeg.toFixed(6)}°. Please select a larger area (min: 0.001° x 0.001°).` },
        { status: 400 }
      );
    }

    // Set up paths for Python script execution
    const rootDir = process.cwd();
    const workspaceDir = path.resolve(rootDir, '..'); // Go up one level from frontend
    const gisDir = path.join(workspaceDir, 'GIS');
    const scriptPath = path.join(gisDir, 'water_quality', 'water_quality_monitor.py');

    console.log('Python script path:', scriptPath);
    
    // Check if Python script exists
    if (!fs.existsSync(scriptPath)) {
      console.error('Water quality analysis script not found at path:', scriptPath);
      return NextResponse.json(
        { error: 'Water quality analysis script not found' },
        { status: 500 }
      );
    }
    
    // Ensure results directory exists
    const resultsDir = path.join(rootDir, 'public', 'results');
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }

    // Create a unique ID for this analysis
    const analysisId = Date.now().toString();
    configPath = path.join(rootDir, `config_${analysisId}.json`);
    const outputImagePath = path.join(resultsDir, `water_quality_${analysisId}.png`);
    const outputDataPath = path.join(resultsDir, `water_quality_${analysisId}.json`);
    
    // Create the config file
    fs.writeFileSync(
      configPath,
      JSON.stringify({
        bboxCoords: body.bboxCoords,
        timeInterval: body.timeInterval,
        dataSource: body.dataSource || 'sentinel2'
      })
    );
    
    console.log('Running analysis with parameters:', {
      bboxCoords: body.bboxCoords,
      timeInterval: body.timeInterval,
      dataSource: body.dataSource || 'sentinel2'
    });
    
    // Get proper Python executable path based on environment
    const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';
    
    // Run the Python script with a timeout of 120 seconds (Sentinel Hub can take longer)
    const pythonCmd = `${pythonExecutable} "${scriptPath}" --config "${configPath}" --output "${outputImagePath}" --data "${outputDataPath}" --debug`;
    console.log('Executing command:', pythonCmd);
    
    try {
      // Set a timeout of 180 seconds for the Python script (increased from 120)
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Python script execution timed out after 180 seconds')), 180000);
      });
      
      // Execute the Python script
      const execResult = await Promise.race([
        execPromise(pythonCmd),
        timeoutPromise
      ]) as { stdout: string, stderr: string };
      
      console.log('Python script output:', execResult.stdout);
      
      if (execResult.stderr && execResult.stderr.trim() !== '') {
        console.error('Python script errors:', execResult.stderr);
      }
      
      // Clean up the config file
      if (configPath && fs.existsSync(configPath)) {
        fs.unlinkSync(configPath);
        configPath = null;
      }
      
      // Check if the output data file was created
      if (!fs.existsSync(outputDataPath)) {
        console.error('Python script did not generate output data file');
        return NextResponse.json(
          { 
            error: 'Failed to analyze water quality: no output data generated',
            details: execResult.stderr || execResult.stdout
          },
          { status: 200 }  // Send 200 instead of 500 to display the error properly
        );
      }
      
      // Read the analysis results
      const analysisData = JSON.parse(fs.readFileSync(outputDataPath, 'utf8'));
      
      // Check if there was an error in the analysis
      if (analysisData.error) {
        console.error('Water quality analysis error:', analysisData.error);
        
        // Return the error with the image created to explain the error
        return NextResponse.json({
          error: analysisData.error,
          imageUrl: `/results/water_quality_${analysisId}.png` // This will be the error image
        }, { status: 200 }); // Return 200 so the error image can be displayed
      }
      
      // Return the results
      return NextResponse.json({
        ndwi_analysis: {
          waterCoverage: analysisData.waterCoverage,
          clearWater: analysisData.clearWater,
          moderateQuality: analysisData.moderateQuality,
          algalPresence: analysisData.algalPresence
        },
        ml_analysis: analysisData.ml_analysis,
        mlAnalysisAvailable: analysisData.mlAnalysisAvailable || false,
        imageUrl: `/results/water_quality_${analysisId}.png`,
        rgbImageUrl: analysisData.rgbImagePath ? 
          `/results/water_quality_${analysisId}_rgb.png` : 
          undefined,
        detailedNdwiUrl: analysisData.detailedNdwiPath ?
          `/results/water_quality_${analysisId}_detailed_ndwi.png` :
          undefined,
        dataSource: analysisData.dataSource,
        trueColorAvailable: analysisData.trueColorAvailable,
        waterDetectionAvailable: analysisData.waterDetectionAvailable
      });
      
    } catch (error) {
      // Clean up the config file
      if (configPath && fs.existsSync(configPath)) {
        fs.unlinkSync(configPath);
        configPath = null;
      }
      
      console.error('Error executing Python script:', error);
      
      // Create a custom error image
      const errorMessage = (error as Error).message;
      const errorImg = path.join(resultsDir, `error_${analysisId}.png`);
      
      // Attempt to create an error visualization file
      try {
        const errorCmd = `${pythonExecutable} -c "
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(10, 6))
plt.text(0.5, 0.5, 'Water Quality Analysis Error:\\n\\n${errorMessage.replace(/"/g, '\\"')}', 
         ha='center', va='center', fontsize=12,
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
plt.axis('off')
plt.savefig('${errorImg.replace(/\\/g, '\\\\')}', dpi=100, bbox_inches='tight')
plt.close(fig)
"`;
        
        await execPromise(errorCmd);
      } catch (imgError) {
        console.error('Failed to create error image:', imgError);
      }
      
      return NextResponse.json(
        { 
          error: 'Failed to analyze water quality: ' + (error as Error).message,
          imageUrl: fs.existsSync(errorImg) ? `/results/error_${analysisId}.png` : null
        },
        { status: 200 } // Return 200 instead of 500 so the client can display the error properly
      );
    }
    
  } catch (error) {
    // Clean up the config file if it exists
    if (configPath && fs.existsSync(configPath)) {
      fs.unlinkSync(configPath);
    }
    
    console.error('Error processing water quality analysis:', error);
    return NextResponse.json(
      { error: 'Failed to process water quality analysis: ' + (error as Error).message },
      { status: 200 } // Return 200 instead of 500 so the client can display the error
    );
  }
} 