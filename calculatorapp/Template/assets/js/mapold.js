$(document).ready(function () {

    var map = L.map('map',{
                                      
    });
    
    map.setView([28.2957487, 83.8123341], 10.5);
    var i=0;
    
    // Add layers to the map
    var googleStreets = L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}',{
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3']
    }).addTo(map);
    var dem = L.tileLayer.wms('http://localhost:9090/geoserver/raster/wms/',{
            layers: "raster:elevation1proj",
            format: 'image/png',
            transparent: true,
            request:"GetMap",
        }).addTo(map);
    
    
    var featureGroup = L.featureGroup().addTo(map);
    
    var drawControl = new L.Control.Draw({
        edit: {
            featureGroup: featureGroup
        },
        draw: {
        polyline: false,
        polygon: {
            allowIntersection: false, // Restricts shapes to simple polygons
            drawError: {
                color: '#FF0000', // 
                message: '<strong>Oh snap!<strong> you can\'t draw that!' //
            },
            shapeOptions: {
                color: '#2653d4'
            }
        },
        circle: false, // Turns off this drawing tool
        rectangle: {
            allowIntersection: false,
            shapeOptions: {
                color: '#2653d4',
                clickable: true
            }
        },
        marker: false,
    }
    }).addTo(map);
    
    
    map.on('draw:created', function(e) {
        var type = e.layerType,
            layer = e.layer;
        
        i=i+1;
    
        layer.bindPopup(type+' id: '+i);
        // layer.bindTooltip(type+' id: '+i, {permanent:true,direction:'center',className: 'wardClassName'});
        
    
        // Each time a feauter is created, it's added to the over arching feature group
        featureGroup.addLayer(e.layer);
    });
    
    
    // on click, clear all layers
    document.getElementById('delete').onclick = function(e) {
        featureGroup.clearLayers();
    }
    document.getElementById('export').onclick = function(e) {
        // Extract GeoJson from featureGroup
        var data = featureGroup.toGeoJSON();
    
        // Stringify the GeoJson
        var convertedData = 'text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(data));
    
        // Create export
        document.getElementById('export').setAttribute('href', 'data:' + convertedData);
        document.getElementById('export').setAttribute('download','data.geojson');
    }
    
    
    document.getElementById('receive').onclick = function(e) {
        
        $.ajax( 
            { 
                type:"GET", 
                url: "call", 
                data:{ 
                            parameter: "min max mean median majority sum"
                }, 
                
            success: function( data ) 
            { 
                loadreceiveddata(data);
                },
            error: function() 
            { 
                alert("Please load data First");
    
                }  
        })  
    }
    document.getElementById('sum').onclick = function(e) {
        
        $.ajax( 
            { 
                type:"GET", 
                url: "call", 
                data:{ 
                            parameter: "sum"
                }, 
                
            success: function( data ) 
            { 
                loadreceiveddata(data);
                },
            error: function() 
            { 
                alert("Please load data First");
    
                } 
        })  
    }
    document.getElementById('min').onclick = function(e) {
        
        $.ajax( 
            { 
                type:"GET", 
                url: "call", 
                data:{ 
                            parameter: "min"
                }, 
                
            success: function( data ) 
            { 
                loadreceiveddata(data);
                },
            error: function() 
            { 
                alert("Please load data First");
    
                }  
        })  
    }
    document.getElementById('max').onclick = function(e) {
        
        $.ajax( 
            { 
                type:"GET", 
                url: "call", 
                data:{ 
                            parameter: "max"
                }, 
                
            success: function( data ) 
            { 
                loadreceiveddata(data);
                },
            error: function() 
            { 
                alert("Please load data First");
    
                }  
        })  
    }
    document.getElementById('mean').onclick = function(e) {
        
        $.ajax( 
            { 
                type:"GET", 
                url: "call", 
                data:{ 
                            parameter: "mean"
                }, 
                
            success: function( data ) 
            { 
                loadreceiveddata(data);
                },
            error: function() 
            { 
                alert("Please load data First");
    
                } 
        })  
    }
    document.getElementById('majority').onclick = function(e) {
        
        $.ajax( 
            { 
                type:"GET", 
                url: "call", 
                data:{ 
                            parameter: "majority"
                }, 
                
            success: function( data ) 
            { 
                
                loadreceiveddata(data);
                
                }, 
            error: function() 
            { 
                alert("Please load data First");
    
                } 
        })  
    }
 
    
    
    document.getElementById('load').onclick = function(e) {
        // Extract GeoJson from featureGroup
        
        var data = featureGroup.toGeoJSON();
        console.log(data);
        
    
        // Stringify the GeoJson
        var convertedData = 'text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(data));
        console.log(JSON.stringify(data));
        if(JSON.stringify(data)=='{"type":"FeatureCollection","features":[]}'){
            alert("Data is null !");
        }else{
                $.ajax( 
                { 
                    type:"GET", 
                    url: "data", 
                    data:{ 
                            vector: JSON.stringify(data) 
                }, 
                success: function( data ) 
                { 
                    alert("Data Loaded Succesfully !");
                    console.log(data);
                    } 
            })
    
        }
        // Create export
        function loadreceiveddata(data){
            alert(data);
            featureGroup.clearLayers();
            var json=JSON.parse(data);
            console.log(json);
           
            var dataLayer=L.geoJson(json,{
                style:{
                    fillColor: " #172f76 ",
                    fillOpacity: 0.9,
                    color:"#ffffff",
                    opacity: 1,
                    weight: 2,
                },
                onEachFeature:function(feature, layer) {
                    
                    layer.on({
                        mouseover: function () {
                            this.setStyle({
                                'fillOpacity':0.3,
                            });
                        },
                        mouseout: function () {
                            this.setStyle({
                                // 'fillColor': ' #ffff01 ',
                                'fillColor': ' #172f76 ',
                                'fillOpacity':0.9,
                            });
                        },
                        click: function (event) {
                            console.log("clicked");
                            console.log(feature.properties);
                        }
                    });
        
                    
                },
            }).addTo(map);
           
           
        
            
        
        }
        
        
    }
    });