package com.thorrpg.prototype;
import android.app.Activity;
import android.app.Presentation;
import android.content.Context;
import android.hardware.display.DisplayManager;
import android.os.Bundle;
import android.view.Display;
import android.view.View;
import android.webkit.WebView;
import android.webkit.WebSettings;
public class MainActivity extends Activity {
 WebView game; Presentation secondary;
 WebView make(Context ctx) { WebView w=new WebView(ctx); WebSettings s=w.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);return w; }
 @Override public void onCreate(Bundle b) {super.onCreate(b);getWindow().getDecorView().setSystemUiVisibility(5894|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
 game=make(this);setContentView(game);game.loadUrl("file:///android_asset/index.html");
 DisplayManager dm=(DisplayManager)getSystemService(Context.DISPLAY_SERVICE);
 Display[] ds=dm.getDisplays(DisplayManager.DISPLAY_CATEGORY_PRESENTATION);
 if(ds.length>0)try {secondary=new Presentation(this,ds[0]);WebView w=make(secondary.getContext());secondary.setContentView(w);secondary.show();w.loadUrl("file:///android_asset/lower.html");}catch(Exception ignored){}
 }
 @Override protected void onDestroy(){if(secondary!=null)secondary.dismiss();if(game!=null)game.destroy();super.onDestroy();}
}