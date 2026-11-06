import Foundation
import AVFoundation
import AppKit
let base=URL(fileURLWithPath:CommandLine.arguments[1])
for name in ["V01","V02","V03","V04","V05"] {
 let asset=AVURLAsset(url:base.appendingPathComponent(name+".mp4"))
 let duration=CMTimeGetSeconds(asset.duration)
 let generator=AVAssetImageGenerator(asset:asset);generator.appliesPreferredTrackTransform=true
 generator.maximumSize=CGSize(width:260,height:400)
 let times=stride(from:0.2,to:duration,by:1.0).map{$0}
 let cols=5;let rows=(times.count+cols-1)/cols;let cellW=270;let cellH=425
 let img=NSImage(size:NSSize(width:cols*cellW,height:rows*cellH));img.lockFocus()
 NSColor.white.setFill();NSRect(x:0,y:0,width:cols*cellW,height:rows*cellH).fill()
 for (i,t) in times.enumerated(){
  if let cg=try? generator.copyCGImage(at:CMTime(seconds:t,preferredTimescale:600),actualTime:nil){
   let x=(i%cols)*cellW;let y=(rows-1-i/cols)*cellH
   NSImage(cgImage:cg,size:.zero).draw(in:NSRect(x:x+5,y:y+22,width:260,height:400))
   (name+" · "+String(format:"%.1fs",t) as NSString).draw(at:NSPoint(x:x+8,y:y+3),withAttributes:[.font:NSFont.systemFont(ofSize:14),.foregroundColor:NSColor.black])
  }
 }
 img.unlockFocus();let rep=NSBitmapImageRep(data:img.tiffRepresentation!)!
 try! rep.representation(using:.png,properties:[:])!.write(to:base.appendingPathComponent(name+"_frames.png"))
 print(name,duration,times.count)
}
