Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile("arena\reports\suppression_core.png")
$bmp = new-object System.Drawing.Bitmap(32, 32)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.DrawImage($img, 0, 0, 32, 32)
$img.Dispose()
$bmp.Save("arena\reports\suppression_core_small.png", [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
$g.Dispose()
Write-Output "Image resized successfully to 32x32"
