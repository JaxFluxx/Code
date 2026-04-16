package innerClass;

import java.time.LocalDate;

public class MainPerson
{

	public static void main(String[] args)
	{
		Person p1=new Person("John Key", "male",LocalDate.parse("1981-05-08"));
		System.out.println(p1.bodyInfo());
		
		Person p2=new Person("李小萌", "女",LocalDate.parse("1984-12-08"));
		Person.Body body =p2.new Body(1.65,50.5);
		body.setHeight(1.68);
		body.personInfo();
		System.out.println("身高："+body.getHeight());
		System.out.println("体重："+body.getWeight());
		Person.Body body2=new Person("张文","男",LocalDate.parse("1976-05-12")).new Body(1.70,60);
		body2.personInfo();
		System.out.println("身高："+body2.getHeight());
		System.out.println("体重："+body2.getWeight());

	}

}
