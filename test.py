def Face_Compare(self, face_images, threshold=0.6):
    try:
        with torch.no_grad():
            
            faces, probs = self.mtcnn(face_images, return_prob=True)

            # Ensure at least one face is detected with 90% confidence
            if faces is not None and len(faces) > 0:
                
                results = []

                for idx, (face, prob) in enumerate(zip(faces, probs)):
                    if prob > 0.95:
                        print(f"Face {idx + 1} detected: {prob * 100:.2f}% confidence")

                        # Calculate embedding for the face
                        emb = self.facenet(face.unsqueeze(0)).detach()

                        match_list = []

                        for emb_db in self.Embeding_List:
                            dist = torch.cdist(emb, emb_db).item()
                            match_list.append(dist)

                        if match_list:
                            min_dist = min(match_list)
                            idx_min = match_list.index(min_dist)

                            percent = self.__face_distance_to_conf(face_distance=min_dist, face_match_threshold=threshold) * 100

                            if min_dist < threshold:
                                results.append((self.Name_List[idx_min], f'{percent:.2f}%'))
                            else:
                                results.append(('No match detected', f'{percent:.2f}%'))
                        else:
                            results.append(('No match detected', 'N/A'))
                    else:
                        results.append(('No match detected', 'N/A'))

                return results

            else:
                return [('No match detected', None)]
        
    except Exception as e:
        print(f"Error: {e}")
        return [('No match detected', None)]
