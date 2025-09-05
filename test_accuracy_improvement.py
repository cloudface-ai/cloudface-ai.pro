"""
test_accuracy_improvement.py - Test accuracy improvements between original and enhanced systems
"""

import os
import time
from typing import List, Dict, Any

def test_original_system():
    """Test the original face recognition system"""
    print("🔍 Testing Original System...")
    
    try:
        from embedding_engine import embed_image_file as original_embed
        from search_engine import rank_matches_for_user as original_search
        
        # Test with sample images
        test_images = []
        if os.path.exists('storage/data'):
            for root, dirs, files in os.walk('storage/data'):
                for file in files[:3]:  # Test first 3 images
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_images.append(os.path.join(root, file))
                        break
                if test_images:
                    break
        
        if not test_images:
            print("⚠️ No test images found")
            return {}
        
        results = {}
        for img_path in test_images:
            start_time = time.time()
            embeddings = original_embed(img_path)
            processing_time = time.time() - start_time
            
            results[os.path.basename(img_path)] = {
                'faces_detected': len(embeddings),
                'processing_time': processing_time,
                'system': 'original'
            }
        
        return results
        
    except Exception as e:
        print(f"❌ Original system test failed: {e}")
        return {}

def test_enhanced_system():
    """Test the enhanced face recognition system"""
    print("🚀 Testing Enhanced System...")
    
    try:
        from enhanced_embedding_engine import embed_image_file_enhanced as enhanced_embed
        
        # Test with same sample images
        test_images = []
        if os.path.exists('storage/data'):
            for root, dirs, files in os.walk('storage/data'):
                for file in files[:3]:  # Test first 3 images
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        test_images.append(os.path.join(root, file))
                        break
                if test_images:
                    break
        
        if not test_images:
            print("⚠️ No test images found")
            return {}
        
        results = {}
        for img_path in test_images:
            start_time = time.time()
            embeddings = enhanced_embed(img_path, use_ai_enhancements=True)
            processing_time = time.time() - start_time
            
            results[os.path.basename(img_path)] = {
                'faces_detected': len(embeddings),
                'processing_time': processing_time,
                'system': 'enhanced'
            }
        
        return results
        
    except Exception as e:
        print(f"❌ Enhanced system test failed: {e}")
        return {}

def compare_results(original_results: Dict, enhanced_results: Dict):
    """Compare results between original and enhanced systems"""
    print("\n📊 COMPARISON RESULTS")
    print("=" * 50)
    
    if not original_results or not enhanced_results:
        print("❌ Cannot compare - missing results")
        return
    
    print(f"{'Image':<20} {'Original':<15} {'Enhanced':<15} {'Improvement':<15}")
    print("-" * 70)
    
    total_original_faces = 0
    total_enhanced_faces = 0
    total_original_time = 0
    total_enhanced_time = 0
    
    for img_name in original_results.keys():
        if img_name in enhanced_results:
            orig = original_results[img_name]
            enh = enhanced_results[img_name]
            
            face_improvement = enh['faces_detected'] - orig['faces_detected']
            time_diff = enh['processing_time'] - orig['processing_time']
            
            print(f"{img_name:<20} {orig['faces_detected']} faces, {orig['processing_time']:.2f}s    {enh['faces_detected']} faces, {enh['processing_time']:.2f}s    {face_improvement:+d} faces, {time_diff:+.2f}s")
            
            total_original_faces += orig['faces_detected']
            total_enhanced_faces += enh['faces_detected']
            total_original_time += orig['processing_time']
            total_enhanced_time += enh['processing_time']
    
    print("-" * 70)
    print(f"{'TOTAL':<20} {total_original_faces} faces, {total_original_time:.2f}s    {total_enhanced_faces} faces, {total_enhanced_time:.2f}s    {total_enhanced_faces - total_original_faces:+d} faces, {total_enhanced_time - total_original_time:+.2f}s")
    
    # Calculate improvements
    face_improvement_pct = ((total_enhanced_faces - total_original_faces) / max(total_original_faces, 1)) * 100
    time_change_pct = ((total_enhanced_time - total_original_time) / max(total_original_time, 0.001)) * 100
    
    print(f"\n📈 SUMMARY:")
    print(f"   Face Detection: {face_improvement_pct:+.1f}% improvement")
    print(f"   Processing Time: {time_change_pct:+.1f}% change")
    
    if total_enhanced_faces > total_original_faces:
        print(f"   ✅ Enhanced system detects {total_enhanced_faces - total_original_faces} more faces!")
    
    if total_enhanced_time < total_original_time:
        print(f"   ✅ Enhanced system is {total_original_time - total_enhanced_time:.2f}s faster!")
    elif total_enhanced_time > total_original_time:
        print(f"   ⚠️ Enhanced system is {total_enhanced_time - total_original_time:.2f}s slower (due to advanced processing)")

def main():
    """Main test function"""
    print("🧪 Face Recognition Accuracy Improvement Test")
    print("=" * 60)
    
    # Test original system
    original_results = test_original_system()
    
    # Test enhanced system
    enhanced_results = test_enhanced_system()
    
    # Compare results
    compare_results(original_results, enhanced_results)
    
    print("\n🎯 RECOMMENDATIONS:")
    if enhanced_results and original_results:
        if any(enhanced_results[img]['faces_detected'] > original_results[img]['faces_detected'] for img in enhanced_results.keys() if img in original_results):
            print("   ✅ Enhanced system shows improved face detection - ready for integration!")
        else:
            print("   ⚠️ No significant improvement detected - may need more testing")
    
    print("   📋 Next steps:")
    print("   1. Test with more diverse images")
    print("   2. Test with different lighting conditions")
    print("   3. Test with different poses and expressions")
    print("   4. Proceed with gradual integration if results are good")

if __name__ == "__main__":
    main()
