import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;

    // TODO: Replace with actual status checking logic
    // This is a mock implementation that randomly generates progress
    const progress = Math.min(Math.floor(Math.random() * 100) + 10, 100);
    const status = progress === 100 ? 'completed' : 'processing';

    return NextResponse.json({
      status,
      progress,
      analysisId: id,
    });
  } catch (error) {
    console.error('Status check error:', error);
    return NextResponse.json(
      { message: 'Failed to check analysis status' },
      { status: 500 }
    );
  }
} 