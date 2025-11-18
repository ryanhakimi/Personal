using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(RawImage))]
[RequireComponent(typeof(AspectRatioFitter))]
public class RawImageAutoFit : MonoBehaviour
{
    RawImage img;
    AspectRatioFitter fitter;
    int lastW, lastH;

    void Awake()
    {
        img = GetComponent<RawImage>();
        fitter = GetComponent<AspectRatioFitter>();
        fitter.aspectMode = AspectRatioFitter.AspectMode.FitInParent;
    }

    void LateUpdate()
    {
        var tex = img.texture;
        if (tex == null) return;
        int w = tex.width, h = tex.height;
        if (w != lastW || h != lastH)
        {
            fitter.aspectRatio = h == 0 ? 1f : (float)w / h;
            lastW = w; lastH = h;
        }
    }
}