declare module 'mapbox-gl' {
  export interface MapboxOptions {
    container: string | HTMLElement;
    style: string;
    center?: [number, number];
    zoom?: number;
    bearing?: number;
    pitch?: number;
    minZoom?: number;
    maxZoom?: number;
    interactive?: boolean;
    attributionControl?: boolean;
    customAttribution?: string | string[];
    logoPosition?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
    renderWorldCopies?: boolean;
    maxBounds?: [[number, number], [number, number]];
    scrollZoom?: boolean;
    dragRotate?: boolean;
    dragPan?: boolean;
    keyboard?: boolean;
    doubleClickZoom?: boolean;
    touchZoomRotate?: boolean;
    trackResize?: boolean;
    bearingSnap?: number;
    pitchWithRotate?: boolean;
    clickTolerance?: number;
    hash?: boolean | string;
    failIfMajorPerformanceCaveat?: boolean;
    preserveDrawingBuffer?: boolean;
    transformRequest?: (url: string, resourceType: string) => {url: string, credentials?: string, headers?: {[key: string]: string}};
    localIdeographFontFamily?: string;
    fadeDuration?: number;
    refreshExpiredTiles?: boolean;
    maxTileCacheSize?: number;
    accessToken?: string;
    locale?: {[key: string]: string};
    cooperativeGestures?: boolean;
  }
  
  export default class Map {
    constructor(options: MapboxOptions);
    addControl(control: any, position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'): this;
    removeControl(control: any): this;
    resize(): this;
    getBounds(): any;
    getContainer(): HTMLElement;
    getCanvas(): HTMLCanvasElement;
    project(lnglat: [number, number]): {x: number, y: number};
    unproject(point: {x: number, y: number}): {lng: number, lat: number};
    on(type: string, listener: Function): this;
    off(type: string, listener: Function): this;
    once(type: string, listener: Function): this;
    getStyle(): any;
    setStyle(style: string | any): this;
    isStyleLoaded(): boolean;
    addSource(id: string, source: any): this;
    removeSource(id: string): this;
    getSource(id: string): any;
    addLayer(layer: any, before?: string): this;
    moveLayer(id: string, beforeId?: string): this;
    removeLayer(id: string): this;
    getLayer(id: string): any;
    setLayerZoomRange(layerId: string, minzoom: number, maxzoom: number): this;
    setPaintProperty(layer: string, property: string, value: any): this;
    setLayoutProperty(layer: string, property: string, value: any): this;
    getZoom(): number;
    setZoom(zoom: number): this;
    zoomTo(zoom: number, options?: {duration?: number, offset?: [number, number], easing?: Function, animate?: boolean}): this;
    zoomIn(options?: {duration?: number}): this;
    zoomOut(options?: {duration?: number}): this;
    getBearing(): number;
    setBearing(bearing: number): this;
    rotateTo(bearing: number, options?: {duration?: number, easing?: Function, animate?: boolean}): this;
    resetNorth(options?: {duration?: number}): this;
    getPitch(): number;
    setPitch(pitch: number): this;
    fitBounds(bounds: [[number, number], [number, number]], options?: {padding?: number | {top: number, bottom: number, left: number, right: number}, linear?: boolean, duration?: number, easing?: Function, offset?: [number, number], maxZoom?: number}): this;
    easeTo(options: {center?: [number, number], zoom?: number, bearing?: number, pitch?: number, around?: [number, number], duration?: number, easing?: Function, offset?: [number, number]}): this;
    jumpTo(options: {center?: [number, number], zoom?: number, bearing?: number, pitch?: number, around?: [number, number]}): this;
    getCenter(): {lng: number, lat: number};
    setCenter(center: [number, number]): this;
    panTo(lnglat: [number, number], options?: {duration?: number, easing?: Function, offset?: [number, number], animate?: boolean}): this;
    panBy(offset: [number, number], options?: {duration?: number, easing?: Function, animate?: boolean}): this;
    getFreeCameraOptions(): any;
    setFreeCameraOptions(options: any): this;
    remove(): void;
    loaded(): boolean;
    isMoving(): boolean;
    isZooming(): boolean;
    isRotating(): boolean;
  }
} 